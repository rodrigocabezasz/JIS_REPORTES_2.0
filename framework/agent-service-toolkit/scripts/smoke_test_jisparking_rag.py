"""Prueba rapida del indice RAG sin arrancar FastAPI ni cargar Settings del servicio.

Uso (con el mismo Python del .venv del toolkit):
  cd framework/agent-service-toolkit
  .venv\\Scripts\\python scripts\\smoke_test_jisparking_rag.py [consulta]

Variables: JIS_RAG_CHROMA_PATH, OLLAMA_EMBED_MODEL, OLLAMA_BASE_URL (opcional)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

_TOOLKIT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    q = " ".join(sys.argv[1:]).strip() or "reglamento interno orden higiene seguridad"
    raw = os.getenv("JIS_RAG_CHROMA_PATH", "chroma_jisparking")
    p = Path(raw)
    persist = p if p.is_absolute() else _TOOLKIT_ROOT / p
    if not persist.is_dir():
        print(f"ERROR: no existe {persist}. Corré primero scripts/build_jisparking_rag.py")
        sys.exit(1)

    model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    base = os.getenv("OLLAMA_BASE_URL", "").strip() or None
    emb = OllamaEmbeddings(model=model, base_url=base) if base else OllamaEmbeddings(model=model)
    store = Chroma(persist_directory=str(persist), embedding_function=emb)
    docs = store.similarity_search(q, k=3)
    print(f"Consulta: {q!r}\n---")
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "?")
        preview = (d.page_content or "")[:500].replace("\n", " ")
        print(f"[{i}] {src}\n    {preview}...\n")


if __name__ == "__main__":
    main()
