"""RAG sobre documentación esencial JIS PARKING (Chroma + embeddings Ollama)."""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings

from core import settings


def _toolkit_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _chroma_dir() -> Path:
    raw = settings.JIS_RAG_CHROMA_PATH
    p = Path(raw)
    return p if p.is_absolute() else _toolkit_root() / raw


def _embeddings() -> OllamaEmbeddings:
    model = settings.OLLAMA_EMBED_MODEL
    if settings.OLLAMA_BASE_URL:
        return OllamaEmbeddings(model=model, base_url=settings.OLLAMA_BASE_URL)
    return OllamaEmbeddings(model=model)


def _retriever():
    persist = str(_chroma_dir())
    if not _chroma_dir().is_dir():
        raise FileNotFoundError(
            f"No existe la base vectorial en {persist}. "
            "Ejecutá el script scripts/build_jisparking_rag.py con documentos en data/jisparking_knowledge/."
        )
    store = Chroma(persist_directory=persist, embedding_function=_embeddings())
    return store.as_retriever(search_kwargs={"k": settings.JIS_RAG_TOP_K})


@tool
def jis_buscar_conocimiento_jisparking(consulta: str) -> str:
    """Busca en la base de conocimiento documental de JIS PARKING (no en MySQL).

    Usar para: glosario, definiciones de negocio, procedimientos operativos, políticas internas,
    criterios de reportes explicados en texto, contexto de producto que no vive en tablas SQL.

    No usar para: totales de ventas, listados de sucursales desde BD, KPIs, depósitos o abonados
    (ahí van las herramientas jis_* de MySQL).

    Args:
        consulta: Pregunta o frases clave en español alineadas a lo que buscás en la documentación.

    Returns:
        Fragmentos relevantes del conocimiento indexado (con ruta de origen en metadatos si está).
    """
    q = (consulta or "").strip()
    if not q:
        return "Consulta vacía: reformulá la pregunta sobre JIS PARKING."
    try:
        docs = _retriever().invoke(q)
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return (
            f"Error al consultar la base vectorial (¿Ollama con modelo de embeddings "
            f"'{settings.OLLAMA_EMBED_MODEL}' y mismo OLLAMA_BASE_URL que el chat?): {e}"
        )
    if not docs:
        return "No se encontraron fragmentos relevantes en la base de conocimiento para esa consulta."
    parts: list[str] = []
    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source") or d.metadata.get("file_path") or "documento"
        parts.append(f"[{i}] (fuente: {src})\n{d.page_content}")
    return "\n\n---\n\n".join(parts)
