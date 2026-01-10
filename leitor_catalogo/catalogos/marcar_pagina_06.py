"""
Marcação da Página 6 - Perfis Tabelados (Tubo Redondo e Tubo Quadrado)
VERSÃO 3 - Marcação mais precisa
"""

import fitz
from PIL import Image, ImageDraw, ImageFont
import io
import os

PDF_PATH = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\catalogo-aluminovo_2025.pdf"
OUTPUT_DIR = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\extracao_conferencia"

def extrair_pagina_como_imagem(pdf_path: str, pagina: int, dpi: int = 150) -> Image.Image:
    doc = fitz.open(pdf_path)
    page = doc[pagina - 1]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    doc.close()
    return img

# Extrair página 6
img = extrair_pagina_como_imagem(PDF_PATH, 6, dpi=150)
draw = ImageDraw.Draw(img)

# Configuração visual
COR_VERDE = "#00DD00"
ESPESSURA = 3

try:
    font = ImageFont.truetype("arial.ttf", 16)
    font_pequena = ImageFont.truetype("arial.ttf", 12)
except:
    font = ImageFont.load_default()
    font_pequena = font

# ========== TUBO REDONDO ==========
# Marcar a TABELA INTEIRA do Tubo Redondo
draw.rectangle([62, 127, 768, 370], outline=COR_VERDE, width=ESPESSURA)
draw.text((775, 130), "TUBO", fill=COR_VERDE, font=font)
draw.text((775, 150), "REDONDO", fill=COR_VERDE, font=font)
draw.text((775, 170), "(12 itens)", fill=COR_VERDE, font=font_pequena)

# ========== TUBO QUADRADO ==========
# Marcar a TABELA INTEIRA do Tubo Quadrado
draw.rectangle([62, 437, 582, 665], outline=COR_VERDE, width=ESPESSURA)
draw.text((590, 440), "TUBO", fill=COR_VERDE, font=font)
draw.text((590, 460), "QUADRADO", fill=COR_VERDE, font=font)
draw.text((590, 480), "(11 itens)", fill=COR_VERDE, font=font_pequena)

# Salvar
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, "pagina_06_marcada.png")
img.save(output_path)
print(f"Salvo: {output_path}")

# ========== DADOS EXTRAÍDOS ==========
tubo_redondo_dados = [
    {"codigo": "TR3/8*100", "kg_m": "0,072", "pol_a": "3/8\"", "pol_e": "-", "mm_a": "9,52", "mm_e": "1,00"},
    {"codigo": "TR3/8*158", "kg_m": "0,108", "pol_a": "3/8\"", "pol_e": "1/16\"", "mm_a": "9,52", "mm_e": "1,58"},
    {"codigo": "TR1/2*158", "kg_m": "0,120", "pol_a": "1/2\"", "pol_e": "1/16\"", "mm_a": "12,70", "mm_e": "1,58"},
    {"codigo": "TR5/8*158", "kg_m": "0,191", "pol_a": "5/8\"", "pol_e": "1/16\"", "mm_a": "15,87", "mm_e": "1,58"},
    {"codigo": "TR3/4*158", "kg_m": "0,186", "pol_a": "3/4\"", "pol_e": "1/16\"", "mm_a": "19,05", "mm_e": "1,58"},
    {"codigo": "TR7/8*158", "kg_m": "0,278", "pol_a": "7/8\"", "pol_e": "1/16\"", "mm_a": "22,22", "mm_e": "1,58"},
    {"codigo": "TR1*158", "kg_m": "0,319", "pol_a": "1\"", "pol_e": "1/16\"", "mm_a": "25,40", "mm_e": "1,58"},
    {"codigo": "TR1.1/4*158", "kg_m": "0,405", "pol_a": "1.1/4\"", "pol_e": "1/16\"", "mm_a": "31,75", "mm_e": "1,58"},
    {"codigo": "TR1.1/2*158", "kg_m": "0,467", "pol_a": "1.1/2\"", "pol_e": "1/16\"", "mm_a": "38,10", "mm_e": "1,50"},
    {"codigo": "TR2*127", "kg_m": "0,506", "pol_a": "2\"", "pol_e": "-", "mm_a": "50,80", "mm_e": "1,20"},
    {"codigo": "TR3*158", "kg_m": "1,003", "pol_a": "3\"", "pol_e": "1/16\"", "mm_a": "76,20", "mm_e": "1,58"},
    {"codigo": "TR4*158", "kg_m": "1,274", "pol_a": "4\"", "pol_e": "1/16\"", "mm_a": "101,60", "mm_e": "1,58"},
]

tubo_quadrado_dados = [
    {"codigo": "1763", "kg_m": "0,190", "pol_a": "1/2\"", "pol_e": "1/16\"", "mm_a": "12,70", "mm_e": "1,58"},
    {"codigo": "1764", "kg_m": "0,233", "pol_a": "5/8\"", "pol_e": "-", "mm_a": "15,87", "mm_e": "1,58"},
    {"codigo": "1751", "kg_m": "0,284", "pol_a": "3/4\"", "pol_e": "-", "mm_a": "19,05", "mm_e": "1,58"},
    {"codigo": "1752", "kg_m": "0,387", "pol_a": "1\"", "pol_e": "-", "mm_a": "25,40", "mm_e": "1,58"},
    {"codigo": "1754", "kg_m": "0,490", "pol_a": "1.1/4\"", "pol_e": "-", "mm_a": "31,75", "mm_e": "1,58"},
    {"codigo": "1756", "kg_m": "0,593", "pol_a": "1.1/2\"", "pol_e": "-", "mm_a": "38,10", "mm_e": "1,58"},
    {"codigo": "1758", "kg_m": "0,801", "pol_a": "2\"", "pol_e": "-", "mm_a": "50,80", "mm_e": "1,58"},
    {"codigo": "1765", "kg_m": "1,609", "pol_a": "3\"", "pol_e": "-", "mm_a": "76,20", "mm_e": "2,00"},
    {"codigo": "TUB4034", "kg_m": "1,526", "pol_a": "-", "pol_e": "-", "mm_a": "80,00", "mm_e": "1,80"},
    {"codigo": "1767L", "kg_m": "2,156", "pol_a": "4\"", "pol_e": "-", "mm_a": "101,60", "mm_e": "2,00"},
    {"codigo": "1767", "kg_m": "2,676", "pol_a": "4\"", "pol_e": "-", "mm_a": "101,60", "mm_e": "2,50"},
]

print("\n" + "="*80)
print("DADOS EXTRAÍDOS - PÁGINA 6 - PERFIS TABELADOS")
print("="*80)

print("\n### TUBO REDONDO (12 itens) ###")
print(f"{'#':<3} {'Código':<12} {'Kg/m':<8} {'Pol A':<10} {'Pol E':<8} {'mm A':<8} {'mm E':<6}")
print("-" * 65)
for i, d in enumerate(tubo_redondo_dados, 1):
    print(f"{i:<3} {d['codigo']:<12} {d['kg_m']:<8} {d['pol_a']:<10} {d['pol_e']:<8} {d['mm_a']:<8} {d['mm_e']:<6}")

print("\n### TUBO QUADRADO (11 itens) ###")
print(f"{'#':<3} {'Código':<12} {'Kg/m':<8} {'Pol A':<10} {'Pol E':<8} {'mm A':<8} {'mm E':<6}")
print("-" * 65)
for i, d in enumerate(tubo_quadrado_dados, 1):
    print(f"{i:<3} {d['codigo']:<12} {d['kg_m']:<8} {d['pol_a']:<10} {d['pol_e']:<8} {d['mm_a']:<8} {d['mm_e']:<6}")

print(f"\nTOTAL: {len(tubo_redondo_dados) + len(tubo_quadrado_dados)} itens")
