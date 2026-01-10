"""
Script para extrair TODAS as páginas do PDF como imagens PNG.
Isso permite trabalhar com as imagens diretamente (mais leve e rápido).
"""

import fitz  # PyMuPDF
from PIL import Image
import io
import os

# Configurações
PDF_PATH = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\catalogo-aluminovo_2025.pdf"
OUTPUT_DIR = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\extracao_conferencia"
DPI = 150  # Qualidade da imagem


def extrair_todas_paginas(pdf_path: str, output_dir: str, dpi: int = 150):
    """Extrai todas as páginas do PDF como imagens PNG."""

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    total = len(doc)

    print(f"PDF: {pdf_path}")
    print(f"Total de páginas: {total}")
    print(f"DPI: {dpi}")
    print(f"Destino: {output_dir}")
    print("-" * 50)

    for i in range(total):
        pagina = i + 1
        page = doc[i]

        # Renderizar página
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        # Converter para PIL e salvar
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        output_path = os.path.join(output_dir, f"pagina_{pagina:02d}_original.png")
        img.save(output_path)

        print(f"[{pagina}/{total}] Extraída: pagina_{pagina:02d}_original.png")

    doc.close()

    print("-" * 50)
    print(f"Concluído! {total} páginas extraídas.")


if __name__ == "__main__":
    extrair_todas_paginas(PDF_PATH, OUTPUT_DIR, DPI)
