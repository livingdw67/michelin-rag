import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "vector_db")

# Ingestion Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# LLM Settings
MODEL_NAME = "gpt-4o"
TEMPERATURE = 0.0
RETRIEVER_K = 25