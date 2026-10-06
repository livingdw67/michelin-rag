FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

# Build the index on first start if it is missing, then launch the app
CMD ["sh", "-c", "[ -f vector_db/chunks.jsonl ] || python -m src.pipeline.index; streamlit run src/ui/app.py --server.port=8501 --server.address=0.0.0.0"]
