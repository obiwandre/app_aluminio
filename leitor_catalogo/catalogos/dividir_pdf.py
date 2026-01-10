"""
Script para dividir PDF grande em partes menores para upload.

Limite de upload: ~10MB
Margem de segurança: dividimos para ~8MB por parte
"""

import os
import fitz  # PyMuPDF

# Configurações
PDF_PATH = r"catalogo-aluminovo_2025.pdf"
OUTPUT_DIR = "catalogo-aluminovo_2025_partes"
MAX_SIZE_MB = 6  # Tamanho máximo por parte em MB (conservador para margem)

def dividir_pdf(pdf_path: str, output_dir: str, max_size_mb: float = 8):
    """Divide um PDF em partes menores baseado no tamanho máximo."""

    # Criar pasta de saída
    os.makedirs(output_dir, exist_ok=True)

    # Abrir PDF original
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)

    print(f"PDF original: {pdf_path}")
    print(f"Tamanho: {file_size_mb:.2f} MB")
    print(f"Total de páginas: {total_pages}")
    print(f"Tamanho máximo por parte: {max_size_mb} MB")
    print("-" * 50)

    # Estimar páginas por MB
    pages_per_mb = total_pages / file_size_mb
    pages_per_part = int(pages_per_mb * max_size_mb)

    # Garantir pelo menos 1 página por parte
    pages_per_part = max(1, pages_per_part)

    print(f"Estimativa: ~{pages_per_mb:.1f} páginas/MB")
    print(f"Páginas por parte: ~{pages_per_part}")
    print("-" * 50)

    # Dividir o PDF
    part_num = 1
    start_page = 0
    partes_criadas = []

    while start_page < total_pages:
        end_page = min(start_page + pages_per_part, total_pages)

        # Criar novo documento com as páginas selecionadas
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)

        # Nome do arquivo de saída
        output_filename = f"parte_{part_num:02d}_pag_{start_page + 1}-{end_page}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        # Salvar
        new_doc.save(output_path)
        part_size_mb = os.path.getsize(output_path) / (1024 * 1024)

        partes_criadas.append({
            "arquivo": output_filename,
            "paginas": f"{start_page + 1}-{end_page}",
            "tamanho_mb": part_size_mb
        })

        print(f"Criado: {output_filename} ({part_size_mb:.2f} MB) - páginas {start_page + 1} a {end_page}")

        new_doc.close()

        start_page = end_page
        part_num += 1

    doc.close()

    print("-" * 50)
    print(f"Divisão completa! {len(partes_criadas)} partes criadas em: {output_dir}")

    # Criar arquivo de índice
    index_path = os.path.join(output_dir, "indice.txt")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(f"Índice do PDF: {pdf_path}\n")
        f.write(f"Total de páginas: {total_pages}\n")
        f.write(f"Tamanho original: {file_size_mb:.2f} MB\n")
        f.write("=" * 50 + "\n\n")
        for parte in partes_criadas:
            f.write(f"{parte['arquivo']}\n")
            f.write(f"  Páginas: {parte['paginas']}\n")
            f.write(f"  Tamanho: {parte['tamanho_mb']:.2f} MB\n\n")

    print(f"Índice salvo em: {index_path}")

    return partes_criadas


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, PDF_PATH)
    output_dir = os.path.join(script_dir, OUTPUT_DIR)

    dividir_pdf(pdf_path, output_dir, MAX_SIZE_MB)
