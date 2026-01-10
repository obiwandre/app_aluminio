"""
Script para extrair página do PDF e marcar itens para conferência.
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import io
import os

# Configurações
PDF_PATH = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\catalogo-aluminovo_2025.pdf"
OUTPUT_DIR = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\extracao_conferencia"

def extrair_pagina_como_imagem(pdf_path: str, pagina: int, dpi: int = 150) -> Image.Image:
    """Extrai uma página do PDF como imagem PIL."""
    doc = fitz.open(pdf_path)
    page = doc[pagina - 1]  # páginas são 0-indexed

    # Renderiza a página como imagem
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)

    # Converte para PIL Image
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))

    doc.close()
    return img


def marcar_areas(img: Image.Image, areas: list, cor: str = "green", espessura: int = 3) -> Image.Image:
    """
    Marca áreas na imagem com retângulos.

    areas: lista de dicts com {x1, y1, x2, y2, label}
    """
    img_marcada = img.copy()
    draw = ImageDraw.Draw(img_marcada)

    # Tenta carregar uma fonte, senão usa padrão
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    for i, area in enumerate(areas, 1):
        x1, y1, x2, y2 = area['x1'], area['y1'], area['x2'], area['y2']
        label = area.get('label', f'Item {i}')

        # Desenha retângulo
        draw.rectangle([x1, y1, x2, y2], outline=cor, width=espessura)

        # Desenha número/label
        draw.text((x1 + 5, y1 - 18), f"{i}", fill=cor, font=font)

    return img_marcada


def salvar_imagem_marcada(img: Image.Image, pagina: int, output_dir: str):
    """Salva a imagem marcada."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"pagina_{pagina:02d}_marcada.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    print(f"Salvo: {filepath}")
    return filepath


if __name__ == "__main__":
    # Teste: extrair página 6
    pagina = 6
    img = extrair_pagina_como_imagem(PDF_PATH, pagina)

    # Por enquanto só salva sem marcação para ver o tamanho/coordenadas
    img.save(os.path.join(OUTPUT_DIR, f"pagina_{pagina:02d}_original.png"))
    print(f"Imagem extraída: {img.size}")
