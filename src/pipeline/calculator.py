"""Exact arithmetic for the agent, plus a check that answers only use grounded numbers.

LLMs are unreliable at arithmetic, so ratios and growth rates are computed here. The
grounding check then confirms every number in a synthesized answer came from a verified
source or a calculator result.
"""
import ast
import operator
import re

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}


def calculate(expression: str) -> float:
    """Safely evaluate an arithmetic expression such as "(1664 / 25992) * 100".

    Only numbers, + - * / **, and parentheses are allowed. Thousands separators are accepted.
    """
    expr = re.sub(r"(?<=\d),(?=\d{3}\b)", "", expression).replace("%", "")

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            if isinstance(node.op, ast.Pow) and abs(ev(node.right)) > 10:
                raise ValueError("Exponent too large")
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"Unsupported expression: {expression}")

    return float(ev(ast.parse(expr, mode="eval")))


_NUMBER = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?")


def numbers_in(text):
    """Numeric values in text, ignoring thousands separators ("25,992" -> 25992.0)."""
    values = []
    for match in _NUMBER.findall(text):
        try:
            values.append(float(match.replace(",", "")))
        except ValueError:
            continue
    return values


def ungrounded_numbers(answer, allowed_text, allowed_values=(), tolerance=0.006):
    """Numbers in the answer that don't appear in the allowed text or values.

    Matching allows rounding (6.4 vs 6.4019), million/billion rescaling (19.7 billion vs 19,676 million),
    and sign flips for reported declines ("-4.4%" vs "fell 4.4%"). Small integers (list counters, counts)
    and years are ignored.
    """
    base = numbers_in(allowed_text) + list(allowed_values)
    pool = base + [v / 1000 for v in base] + [v * 1000 for v in base]
    missing = []
    for value in numbers_in(answer):
        if abs(value) < 10 and float(value).is_integer():
            continue  # list numbers, counts like "two companies", footnote markers
        if 1900 <= value <= 2100 and float(value).is_integer():
            continue  # years
        if not any(_close(value, p, tolerance) or _close(-value, p, tolerance) for p in pool):
            missing.append(value)
    return missing


def _close(a, b, tolerance):
    if b == 0:
        return a == 0
    if abs(a - b) / abs(b) <= tolerance:
        return True
    # Rounded presentations: 6.4 vs 6.4017, 19.7 vs 19.676 billion shown as 19.7
    for digits in (0, 1, 2):
        if round(b, digits) == a:
            return True
    return False
