"""Construye Chroma para JIS PARKING con embeddings de Ollama (mismo servidor que el LLM).

Uso (desde la raíz del toolkit, ej. framework/agent-service-toolkit):

  Windows (recomendado: crea .venv e instala deps):
    .\\scripts\\run_build_jisparking_rag.ps1

  Manual:
    .venv\\Scripts\\activate
    pip install -e .
    ollama pull nomic-embed-text
    python scripts/build_jisparking_rag.py

Documentos: carpeta data/jisparking_knowledge/ — .md, .txt, .pdf, .docx.
  Imágenes (fotos de carteles): usar scripts/image_to_jisparking_knowledge.py (OCR) o transcribir a .md/.txt.
Salida: directorio configurado en JIS_RAG_CHROMA_PATH (default chroma_jisparking junto a src/).
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # Sin venv del toolkit: las variables deben estar en el entorno del sistema.
    pass

from langchain_chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Raíz del paquete toolkit (donde están src/ y scripts/)
_TOOLKIT_ROOT = Path(__file__).resolve().parents[1]


def _data_dir() -> Path:
    return _TOOLKIT_ROOT / "data" / "jisparking_knowledge"


def _persist_dir() -> Path:
    raw = os.getenv("JIS_RAG_CHROMA_PATH", "chroma_jisparking")
    p = Path(raw)
    return p if p.is_absolute() else _TOOLKIT_ROOT / p


def _ollama_embed_model() -> str:
    return os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")


def _ollama_base_url() -> str | None:
    u = os.getenv("OLLAMA_BASE_URL", "").strip()
    return u or None


def _ollama_display_url() -> str:
    return _ollama_base_url() or "http://127.0.0.1:11434 (default Ollama local)"


def _preflight_ollama_embeddings(embeddings: OllamaEmbeddings, model: str) -> None:
    """Evita borrar Chroma si Ollama no responde o falta el modelo de embeddings."""
    try:
        embeddings.embed_query("ping")
    except Exception as e:
        raise SystemExit(
            "No se pudo conectar a Ollama para generar embeddings.\n\n"
            f"  Modelo: {model}\n"
            f"  URL: {_ollama_display_url()}\n\n"
            "Qué revisar:\n"
            "  • Windows: abrí la app **Ollama** (debe quedar en la bandeja; sin eso no hay servidor en :11434).\n"
            "  • En terminal: `ollama serve` (si no usás la app) y `ollama pull "
            + model
            + "`\n"
            "  • Si Ollama corre en **otra PC o JISLAB**: en `.env` del toolkit definí\n"
            "      OLLAMA_BASE_URL=http://IP_O_HOST:11434\n"
            "    (la misma que usás para el agente / chat).\n\n"
            f"Detalle técnico: {e}"
        ) from None


def _load_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path)).load()
    if suffix == ".docx":
        return Docx2txtLoader(str(path)).load()
    if suffix in (".md", ".txt"):
        return TextLoader(str(path), encoding="utf-8").load()
    return []


def build(
    source_dir: Path | None = None,
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
    reset: bool = True,
) -> Chroma:
    folder = source_dir or _data_dir()
    if not folder.is_dir():
        raise SystemExit(
            f"Creá la carpeta y colocá ahí los documentos: {folder}\n"
            "(archivos .md, .txt, .pdf o .docx con lo esencial de JIS PARKING)."
        )

    persist = _persist_dir()
    model = _ollama_embed_model()
    base = _ollama_base_url()
    if base:
        embeddings = OllamaEmbeddings(model=model, base_url=base)
    else:
        embeddings = OllamaEmbeddings(model=model)

    print(f"Comprobando Ollama (embeddings) en {_ollama_display_url()} …")
    _preflight_ollama_embeddings(embeddings, model)

    if reset and persist.exists():
        shutil.rmtree(persist)
        print(f"Eliminada base anterior: {persist}")

    chroma = Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist),
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    added = 0
    for name in sorted(os.listdir(folder)):
        file_path = folder / name
        if not file_path.is_file():
            continue
        docs = _load_file(file_path)
        if not docs:
            print(f"Omitido (tipo no soportado): {name}")
            continue
        for d in docs:
            d.metadata.setdefault("source", str(file_path.name))
        chunks = splitter.split_documents(docs)
        if chunks:
            chroma.add_documents(chunks)
            added += len(chunks)
            print(f"{name}: {len(chunks)} chunks")

    if added == 0:
        raise SystemExit("No se indexó ningún documento. Revisá formatos y la carpeta de datos.")

    print(f"Listo: {added} chunks en {persist} (embeddings: {model}).")
    return chroma


if __name__ == "__main__":
    build()
