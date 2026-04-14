"""Pasa una imagen (cartel, foto de póster, captura) a texto para el RAG de JIS PARKING.

El índice Chroma solo ingiere texto (.md, .txt, .pdf con texto real). Las fotos son mapas de píxeles:
hay que extraer texto con OCR o transcribir a mano.

Opción A — Sin Python (rápido):
  - Word: insertar imagen → clic derecho → copiar texto de la imagen (si está disponible).
  - Google Drive: subir PNG/PDF → abrir con Google Docs → se genera texto editable → copiar a un .txt.

Opción B — Este script (Tesseract OCR en Windows):
  1. Instalar Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
     Ejecutable típico: C:\\Program Files\\Tesseract-OCR\\tesseract.exe
  2. En el instalador, incluir datos de idioma **Spanish** (spa).
  3. En el venv del toolkit:
       pip install pytesseract pillow
     (o: uv sync --group rag_ocr  si usás el grupo del pyproject)
  4. Si hace falta, variable de entorno:
       TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
  5. Ejecutar desde la raíz del toolkit:
       python scripts/image_to_jisparking_knowledge.py "C:\\ruta\\protocolo.png"
  6. Regenerar el índice:
       .\\scripts\\run_build_jisparking_rag.ps1
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_TOOLKIT_ROOT = Path(__file__).resolve().parents[1]
_OUT_DIR = _TOOLKIT_ROOT / "data" / "jisparking_knowledge"


def _default_tesseract_cmd() -> str | None:
    exe = os.environ.get("TESSERACT_CMD", "").strip()
    if exe and Path(exe).is_file():
        return exe
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if Path(candidate).is_file():
            return candidate
    return None


def main() -> None:
    p = argparse.ArgumentParser(description="OCR de imagen → .txt en data/jisparking_knowledge/")
    p.add_argument("imagen", type=Path, help="Ruta a .png, .jpg, .jpeg, .webp, .tif")
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Archivo .txt de salida (default: nombre derivado en jisparking_knowledge)",
    )
    p.add_argument(
        "--lang",
        default="spa+eng",
        help="Idiomas Tesseract, ej. spa+eng (requiere spa.traineddata instalado)",
    )
    args = p.parse_args()

    img: Path = args.imagen
    if not img.is_file():
        print(f"No existe el archivo: {img}", file=sys.stderr)
        sys.exit(1)

    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        print(
            "Faltan dependencias. En el venv del toolkit ejecutá:\n"
            "  pip install pytesseract pillow\n"
            "O instalá el grupo: uv sync --group rag_ocr",
            file=sys.stderr,
        )
        raise SystemExit(1) from e

    tess = _default_tesseract_cmd()
    if tess:
        pytesseract.pytesseract.tesseract_cmd = tess
    else:
        print(
            "No se encontró tesseract.exe. Instalá Tesseract (enlace en la cabecera de este script) "
            "o definí la variable de entorno TESSERACT_CMD con la ruta completa al .exe.",
            file=sys.stderr,
        )
        sys.exit(1)

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^\w\-]+", "-", img.stem.lower()).strip("-") or "documento-imagen"
    out_path = args.out or (_OUT_DIR / f"{stem}-ocr-{datetime.now().strftime('%Y%m%d')}.txt")

    image = Image.open(img)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    text = pytesseract.image_to_string(image, lang=args.lang)
    text = (text or "").strip()
    if not text:
        print(
            "OCR devolvió texto vacío. Probá: imagen más nítida, zoom mayor, o idioma --lang spa "
            "(verifica que spa.traineddata exista en tessdata).",
            file=sys.stderr,
        )
        sys.exit(2)

    header = (
        f"# Texto extraído por OCR desde: {img.name}\n"
        f"# Fecha: {datetime.now().isoformat(timespec='seconds')}\n"
        f"# Revisar y corregir errores antes de confiar en el contenido para el chatbot.\n\n"
    )
    out_path.write_text(header + text, encoding="utf-8")
    print(f"Escrito: {out_path} ({len(text)} caracteres de texto OCR).")
    print("Siguiente paso: .\\scripts\\run_build_jisparking_rag.ps1")


if __name__ == "__main__":
    main()
