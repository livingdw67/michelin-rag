"""LangGraph agent that routes questions and decomposes comparisons.

Simple questions go straight to the verified RAG pipeline. Comparisons and multi-metric
questions are split into single-company, single-fact sub-questions, each answered and
citation-verified independently, then combined. Arithmetic goes through a calculator tool,
and a final check confirms every number in the combined answer is grounded.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Literal, Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from config.settings import settings
from src.pipeline.answer import SYSTEM_PROMPT, answer_question
from src.pipeline.calculator import calculate, ungrounded_numbers
from src.pipeline.guardrails import GuardrailError, check_question, classify_input, leaks_prompt
from src.pipeline.retrieval import get_retriever

MAX_SUB_QUESTIONS = 8
MAX_TOOL_ROUNDS = 5

CONTEXTUALIZE_PROMPT = """Rewrite the latest question so it can be understood without the conversation. \
Resolve references like "they", "that company", or "the same metric". If it is already standalone, return it unchanged.

Conversation:
{history}

Latest question: {question}"""

PLAN_PROMPT = """You plan how to answer questions about four tire companies' 2025 annual reports \
(Michelin, Goodyear, Continental, Bridgestone).

Choose route "single" if the question asks about one company (any number of closely related facts that \
one search can find), or is general/off-topic. Choose "multi" if it compares companies or asks for several \
distinct metrics. For "multi", write sub-questions that each name exactly ONE company and ONE metric, are fully \
self-contained, and keep the question's year. Do not answer the question.

Question: {question}"""

SYNTHESIZE_PROMPT = """Combine the verified sub-answers below into one answer to the user's question.

Rules:
1. Use ONLY facts stated in the sub-answers. Never add outside knowledge.
2. For any arithmetic (differences, ratios, growth rates, margins), call the `calculate` tool. Never do math yourself.
3. If a sub-answer says information was not found, say which part is missing instead of guessing.
4. Keep units and currencies as reported. Do not convert currencies. Use a Markdown table for comparisons.
5. Only calculate what the question asks for or what is needed to answer it (e.g. "which is larger" may need \
one difference). Round percentages to one decimal and ratios to two decimals.
6. Be concise: no closing offers or suggestions. Do not include citations or chunk ids; sources are attached \
separately."""


class SubQuestion(BaseModel):
    company: Optional[str] = Field(description="Michelin, Goodyear, Continental, Bridgestone, or null")
    question: str


class Plan(BaseModel):
    route: Literal["single", "multi"]
    sub_questions: list[SubQuestion] = Field(default_factory=list)


@tool
def calculate_tool(expression: str) -> str:
    """Evaluate an arithmetic expression exactly, e.g. "(1664 / 25992) * 100". Use for every calculation."""
    try:
        return f"{calculate(expression):.6g}"
    except Exception as e:
        return f"error: {e}"


calculate_tool.name = "calculate"


class AgentState(TypedDict, total=False):
    question: str
    history: list
    standalone: str
    route: str
    sub_questions: list
    sub_results: list
    calculations: list
    status: str
    answer: str
    sources: list
    ungrounded: list


@dataclass
class AgentResult:
    question: str
    status: str
    answer: str
    sources: list = field(default_factory=list)
    route: str = "single"
    sub_results: list = field(default_factory=list)
    calculations: list = field(default_factory=list)
    ungrounded: list = field(default_factory=list)
    retrieved: list = field(default_factory=list)
    rejected_citations: int = 0


def _llm(model=None, **kwargs):
    return ChatOpenAI(model=model or settings.chat_model, api_key=settings.openai_api_key, **kwargs)


def contextualize(state: AgentState):
    history = state.get("history") or []
    if not history:
        return {"standalone": state["question"]}
    transcript = "\n".join(f"{role}: {text}" for role, text in history[-6:])
    rewritten = _llm(settings.rewrite_model).invoke(
        CONTEXTUALIZE_PROMPT.format(history=transcript, question=state["question"])).content.strip()
    return {"standalone": rewritten or state["question"]}


def plan(state: AgentState):
    result = _llm(reasoning_effort="low").with_structured_output(Plan).invoke(
        PLAN_PROMPT.format(question=state["standalone"]))
    subs = [s.question for s in result.sub_questions][:MAX_SUB_QUESTIONS]
    if result.route == "multi" and len(subs) >= 2:
        return {"route": "multi", "sub_questions": subs}
    return {"route": "single", "sub_questions": []}


def answer_single(state: AgentState):
    result = answer_question(state["standalone"], retriever=get_retriever())
    return {"status": result.status, "answer": result.answer, "sources": result.sources, "sub_results": [result]}


def answer_subs(state: AgentState):
    retriever = get_retriever()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda q: answer_question(q, retriever=retriever), state["sub_questions"]))
    return {"sub_results": results}


def synthesize(state: AgentState):
    results = state["sub_results"]
    answered = [r for r in results if r.status == "answered"]
    sources = list({s["chunk_id"]: s for r in answered for s in r.sources}.values())
    if not answered:
        missing = "; ".join(r.question for r in results)
        return {"status": "not_found", "answer": f"The reports don't support an answer to: {missing}",
                "sources": [], "calculations": [], "ungrounded": []}

    brief = "\n\n".join(f"Sub-question: {r.question}\nStatus: {r.status}\nAnswer: {r.answer}" for r in results)
    messages = [SystemMessage(SYNTHESIZE_PROMPT),
                HumanMessage(f"User question: {state['standalone']}\n\nVerified sub-answers:\n\n{brief}")]
    # Tool calling with reasoning requires the Responses API for this model family
    llm = _llm(reasoning_effort="low", use_responses_api=True).bind_tools([calculate_tool])
    calculations = []
    for _ in range(MAX_TOOL_ROUNDS):
        reply = llm.invoke(messages)
        messages.append(reply)
        if not reply.tool_calls:
            break
        for call in reply.tool_calls:
            output = calculate_tool.invoke(call["args"])
            calculations.append({"expression": call["args"].get("expression", ""), "result": output})
            messages.append(ToolMessage(output, tool_call_id=call["id"]))
    answer = reply.text

    # Grounding check: every number must come from a sub-answer, a cited quote, or the calculator
    allowed_text = brief + " " + " ".join(s["quote"] for s in sources) + " " + state["standalone"]
    allowed_values = [float(c["result"]) for c in calculations if not c["result"].startswith("error")]
    ungrounded = ungrounded_numbers(answer, allowed_text, allowed_values)
    if ungrounded:
        # Fall back to the verified sub-answers rather than show an unsupported number
        answer = ("I couldn't verify every figure in a combined summary, so here are the verified answers "
                  "to each part:\n\n" + "\n\n".join(f"**{r.question}**\n\n{r.answer}" for r in results))
    return {"status": "answered", "answer": answer, "sources": sources,
            "calculations": calculations, "ungrounded": ungrounded}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("contextualize", contextualize)
    graph.add_node("plan", plan)
    graph.add_node("answer_single", answer_single)
    graph.add_node("answer_subs", answer_subs)
    graph.add_node("synthesize", synthesize)
    graph.add_edge(START, "contextualize")
    graph.add_edge("contextualize", "plan")
    graph.add_conditional_edges("plan", lambda s: s["route"], {"single": "answer_single", "multi": "answer_subs"})
    graph.add_edge("answer_single", END)
    graph.add_edge("answer_subs", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()


_GRAPH = None


def run_agent(question, history=None):
    """Answer a question with routing, decomposition, verified citations, and grounded arithmetic."""
    global _GRAPH
    question = check_question(question)  # layer 1: fast pattern checks
    if settings.llm_input_classifier:  # layer 2: small-model classifier
        previous = next((text for role, text in reversed(history or []) if role == "user"), "")
        category = classify_input(f"{question}\n(Previous question in this conversation: {previous})"
                                  if previous else question)
        if category == "injection":
            raise GuardrailError("This assistant only answers questions about the tire company reports.")
        if category == "off_topic":
            return AgentResult(question=question, status="out_of_scope", route="classifier",
                               answer="I can only answer questions about the four companies' 2025 annual reports.")
    _GRAPH = _GRAPH or build_graph()
    state = _GRAPH.invoke({"question": question, "history": history or []})
    if leaks_prompt(state["answer"], [SYSTEM_PROMPT, PLAN_PROMPT, SYNTHESIZE_PROMPT]):  # layer 3: output guard
        raise GuardrailError("This assistant only answers questions about the tire company reports.")
    subs = state.get("sub_results", [])
    return AgentResult(
        question=question, status=state["status"], answer=state["answer"], sources=state.get("sources", []),
        route=state["route"], sub_results=subs, calculations=state.get("calculations", []),
        ungrounded=state.get("ungrounded", []),
        retrieved=[d for r in subs for d in r.retrieved],
        rejected_citations=sum(r.rejected_citations for r in subs))
