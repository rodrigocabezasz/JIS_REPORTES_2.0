#!/usr/bin/env python3
"""
Ejecuta las frases de docs/PREGUNTAS_CHATBOT_REVISADAS.md contra el grafo jis-reports (LLM + tools).

Uso (desde la raíz del repo, con venv y .env cargados como en instrucciones.txt):
  python scripts/regression_chatbot_preguntas.py
  python scripts/regression_chatbot_preguntas.py --max 10
  python scripts/regression_chatbot_preguntas.py --dry-run

Requiere: Ollama/servidor LLM según .env del toolkit, MySQL si las tools deben completar (sin DB verás errores en tool).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
import uuid
from pathlib import Path

# Raíz repo → toolkit src en PYTHONPATH
_REPO = Path(__file__).resolve().parents[1]
_TOOLKIT_SRC = _REPO / "framework" / "agent-service-toolkit" / "src"
if str(_TOOLKIT_SRC) not in sys.path:
    sys.path.insert(0, str(_TOOLKIT_SRC))
os.chdir(_TOOLKIT_SRC)


def _load_dotenv_files() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(_REPO / ".env")
    load_dotenv(_TOOLKIT_SRC.parent / ".env")


def parse_questions(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding="utf-8")
    out: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith(("- ", "* ")):
            continue
        m = re.match(r'^[-*]\s*"([^"]+)"', line)
        if not m:
            m = re.match(r"^[-*]\s*\u201c([^\u201d]+)\u201d", line)
        if not m:
            continue
        q = m.group(1).strip()
        if not q or len(q) < 8:
            continue
        out.append(normalize_question(q))
    return out


def normalize_question(q: str) -> str:
    q = q.replace("[número]", "42")
    q = q.replace("[fragmento del nombre del local]", "Florida")
    q = q.replace("[nombre o id]", "Florida")
    q = q.replace("[nombre]", "David Gómez")
    q = q.replace("…", "12345678")
    q = re.sub(r"\bmes actual\b", "marzo 2026", q, flags=re.I)
    return q


def tools_from_state(messages: list) -> list[str]:
    from langchain_core.messages import AIMessage, ToolMessage

    names: list[str] = []
    for m in messages:
        if isinstance(m, ToolMessage) and getattr(m, "name", None):
            names.append(str(m.name))
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                if isinstance(tc, dict):
                    n = tc.get("name")
                else:
                    n = getattr(tc, "name", None)
                if n:
                    names.append(str(n))
    # de-duplicar conservando orden
    seen: set[str] = set()
    uniq: list[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


async def run_question(graph, question: str, model: str | None) -> tuple[list[str], str, bool]:
    from langchain_core.messages import AIMessage, HumanMessage

    cfg: dict = {
        "configurable": {"thread_id": str(uuid.uuid4())},
        "recursion_limit": 60,
    }
    if model:
        cfg["configurable"]["model"] = model

    state = await graph.ainvoke({"messages": [HumanMessage(content=question)]}, cfg)
    msgs = state.get("messages", [])
    tools = tools_from_state(msgs)
    last = msgs[-1] if msgs else None
    content = ""
    if isinstance(last, AIMessage):
        c = last.content
        content = c if isinstance(c, str) else str(c)
    err = "success" not in content.lower() and (
        "Indica periodo" in content
        or "Faltan variables" in content
        or "No se pudo conectar al modelo" in content
    )
    return tools, content[:400], err


async def main_async() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=0, help="Máximo de preguntas (0 = todas)")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar preguntas parseadas")
    parser.add_argument("--model", type=str, default=None, help="Override modelo (configurable.model)")
    args = parser.parse_args()

    md = _REPO / "docs" / "PREGUNTAS_CHATBOT_REVISADAS.md"
    if not md.is_file():
        print(f"No existe {md}")
        return 2

    questions = parse_questions(md)
    if args.dry_run:
        print(f"Preguntas parseadas: {len(questions)}")
        for i, q in enumerate(questions[:20], 1):
            print(f"  {i}. {q[:100]}...")
        if len(questions) > 20:
            print(f"  ... +{len(questions) - 20} más")
        return 0

    _load_dotenv_files()

    from agents.jis_reports_agent import jis_reports_agent

    graph = jis_reports_agent
    limit = args.max if args.max > 0 else len(questions)
    subset = questions[:limit]

    print(f"Ejecutando {len(subset)} preguntas (de {len(questions)} en el MD)...\n")
    fails = 0
    for i, q in enumerate(subset, 1):
        try:
            tools, preview, suspicious = await run_question(graph, q, args.model)
            flag = " ??" if suspicious else ""
            print(f"[{i}/{len(subset)}] tools={tools}{flag}")
            print(f"    Q: {q[:120]}{'...' if len(q) > 120 else ''}")
            if suspicious:
                print(f"    preview: {preview[:200]}...")
                fails += 1
        except Exception as e:
            fails += 1
            print(f"[{i}/{len(subset)}] ERROR: {e}")
            print(f"    Q: {q[:120]}")
    print(f"\nListo. Con errores/sospechosos: {fails}/{len(subset)}")
    return 1 if fails else 0


def main() -> None:
    raise SystemExit(asyncio.run(main_async()))


if __name__ == "__main__":
    main()
