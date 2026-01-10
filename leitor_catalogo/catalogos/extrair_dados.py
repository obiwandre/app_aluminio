"""
Pipeline de Extração de Dados do Catálogo
==========================================
Extrai os dados das áreas marcadas e prepara para validação.

Fluxo:
1. Carrega marcacoes.json
2. Recorta as áreas marcadas (NOME, IMAGEM, TABELA)
3. Salva as imagens recortadas para análise
4. Gera arquivo de dados com estrutura para preenchimento

A extração final é feita manualmente (Claude lê as imagens)
para garantir 100% de precisão nos dados críticos.
"""

import json
import os
from PIL import Image
import re

# Configurações
IMAGENS_DIR = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\extracao_conferencia"
MARCACOES_FILE = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\marcacoes.json"
DADOS_FILE = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\dados_catalogo.json"
RECORTES_DIR = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\recortes"


def carregar_marcacoes():
    """Carrega o arquivo de marcações."""
    with open(MARCACOES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_imagem_pagina(pagina: int) -> Image.Image:
    """Carrega a imagem original de uma página."""
    caminho = os.path.join(IMAGENS_DIR, f"pagina_{pagina:02d}_original.png")
    return Image.open(caminho)


def recortar_area(img: Image.Image, coords: list) -> Image.Image:
    """Recorta uma área da imagem baseado nas coordenadas [x1, y1, x2, y2]."""
    return img.crop(coords)


def nome_seguro(texto: str) -> str:
    """Converte texto para nome de arquivo seguro."""
    return re.sub(r'[^\w\-]', '_', texto)


def recortar_e_salvar(pagina: int, dados_pagina: dict):
    """Recorta todas as áreas marcadas de uma página e salva."""
    categoria = dados_pagina.get("categoria") or "sem_categoria"
    itens = dados_pagina.get("itens", [])

    if not itens:
        return None

    print(f"\n{'='*60}")
    print(f"Página {pagina} - Categoria: {categoria}")
    print(f"{'='*60}")

    # Carregar imagem
    img = carregar_imagem_pagina(pagina)

    # Criar pasta para recortes desta página
    pasta_pagina = os.path.join(RECORTES_DIR, f"pag{pagina:02d}_{nome_seguro(categoria)}")
    os.makedirs(pasta_pagina, exist_ok=True)

    resultado = {
        "pagina": pagina,
        "categoria": categoria,
        "itens": []
    }

    for item in itens:
        nome_item = item.get("nome")
        marcacoes = item.get("marcacoes", {})

        print(f"\n  Item: {nome_item}")

        item_dados = {
            "nome": nome_item,
            "arquivos": {},
            "dados_extraidos": {
                "nome_extraido": None,
                "tabela": {
                    "cabecalho": [],
                    "linhas": []
                }
            }
        }

        nome_base = nome_seguro(nome_item)

        # Recortar e salvar NOME
        if marcacoes.get("nome"):
            coords = marcacoes["nome"]
            img_nome = recortar_area(img, coords)
            caminho = os.path.join(pasta_pagina, f"{nome_base}_NOME.png")
            img_nome.save(caminho)
            item_dados["arquivos"]["nome"] = caminho
            print(f"    -> {nome_base}_NOME.png")

        # Recortar e salvar IMAGEM
        if marcacoes.get("imagem"):
            coords = marcacoes["imagem"]
            img_perfil = recortar_area(img, coords)
            caminho = os.path.join(pasta_pagina, f"{nome_base}_IMAGEM.png")
            img_perfil.save(caminho)
            item_dados["arquivos"]["imagem"] = caminho
            print(f"    -> {nome_base}_IMAGEM.png")

        # Recortar e salvar TABELA
        if marcacoes.get("tabela"):
            coords = marcacoes["tabela"]
            img_tabela = recortar_area(img, coords)
            caminho = os.path.join(pasta_pagina, f"{nome_base}_TABELA.png")
            img_tabela.save(caminho)
            item_dados["arquivos"]["tabela"] = caminho
            print(f"    -> {nome_base}_TABELA.png")

        resultado["itens"].append(item_dados)

    return resultado


def executar_recortes():
    """Executa o recorte de todas as áreas marcadas."""
    print("="*60)
    print("PIPELINE DE RECORTE - CATÁLOGO ALUMINOVO 2025")
    print("="*60)

    # Carregar marcações
    marcacoes = carregar_marcacoes()

    # Filtrar páginas que têm itens
    paginas_com_dados = {
        pag: dados for pag, dados in marcacoes.items()
        if dados.get("itens")
    }
    print(f"\nPáginas com itens marcados: {len(paginas_com_dados)}")

    # Criar pasta de recortes
    os.makedirs(RECORTES_DIR, exist_ok=True)

    # Processar cada página
    resultados = []
    for pag_str, dados in paginas_com_dados.items():
        pagina = int(pag_str)
        resultado = recortar_e_salvar(pagina, dados)
        if resultado:
            resultados.append(resultado)

    # Salvar estrutura de dados (para preenchimento posterior)
    with open(DADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"RECORTES CONCLUÍDOS!")
    print(f"{'='*60}")
    print(f"Recortes salvos em: {RECORTES_DIR}")
    print(f"Estrutura de dados em: {DADOS_FILE}")
    print(f"\nPróximo passo: Claude analisa as imagens e preenche os dados.")

    return resultados


# ============================================================
# DADOS EXTRAÍDOS MANUALMENTE (Claude lê as imagens)
# ============================================================

DADOS_PAGINA_6 = {
    "pagina": 6,
    "categoria": "Perfis Tabelados",
    "itens": [
        {
            "nome": "Tubo Redondo",
            "tabela": {
                "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada E", "Milímetro A", "Milímetro E"],
                "linhas": [
                    ["TR3/8*100", "0,072", "3/8\"", "-", "9,52", "1,00"],
                    ["TR3/8*158", "0,108", "3/8\"", "1/16\"", "9,52", "1,58"],
                    ["TR1/2*158", "0,120", "1/2\"", "1/16\"", "12,70", "1,58"],
                    ["TR5/8*158", "0,191", "5/8\"", "1/16\"", "15,87", "1,58"],
                    ["TR3/4*158", "0,186", "3/4\"", "1/16\"", "19,05", "1,58"],
                    ["TR7/8*158", "0,278", "7/8\"", "1/16\"", "22,22", "1,58"],
                    ["TR1*158", "0,319", "1\"", "1/16\"", "25,40", "1,58"],
                    ["TR1.1/4*158", "0,405", "1.1/4\"", "1/16\"", "31,75", "1,58"],
                    ["TR1.1/2*158", "0,467", "1.1/2\"", "1/16\"", "38,10", "1,50"],
                    ["TR2*127", "0,506", "2\"", "-", "50,80", "1,20"],
                    ["TR3*158", "1,003", "3\"", "1/16\"", "76,20", "1,58"],
                    ["TR4*158", "1,274", "4\"", "1/16\"", "101,60", "1,58"],
                ]
            }
        },
        {
            "nome": "Tubo Quadrado",
            "tabela": {
                "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada E", "Milímetro A", "Milímetro E"],
                "linhas": [
                    ["1763", "0,190", "1/2\"", "1/16\"", "12,70", "1,58"],
                    ["1764", "0,233", "5/8\"", "-", "15,87", "1,58"],
                    ["1751", "0,284", "3/4\"", "-", "19,05", "1,58"],
                    ["1752", "0,387", "1\"", "-", "25,40", "1,58"],
                    ["1754", "0,490", "1.1/4\"", "-", "31,75", "1,58"],
                    ["1756", "0,593", "1.1/2\"", "-", "38,10", "1,58"],
                    ["1758", "0,801", "2\"", "-", "50,80", "1,58"],
                    ["1765", "1,609", "3\"", "-", "76,20", "2,00"],
                    ["TUB4034", "1,526", "-", "-", "80,00", "1,80"],
                    ["1767L", "2,156", "4\"", "-", "101,60", "2,00"],
                    ["1767", "2,676", "4\"", "-", "101,60", "2,50"],
                ]
            }
        }
    ]
}


DADOS_PAGINA_7 = {
    "pagina": 7,
    "categoria": "Perfis Tabelados",
    "itens": [
        {
            "nome": "Tubo Retangular",
            "tabela": {
                "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada B", "Polegada E", "Milímetro A", "Milímetro B", "Milímetro E"],
                "linhas": [
                    ["1704L", "0,230", "1/2\"", "1\"", "-", "12,70", "25,40", "1,20"],
                    ["1704", "0,300", "1/2\"", "1\"", "1/16\"", "12,70", "25,40", "1,58"],
                    ["1713", "0,497", "-", "-", "-", "30,00", "20,00", "2,00"],
                    ["1702", "0,904", "3\"", "1.1/2\"", "-", "76,20", "38,10", "1,50"],
                    ["1707", "0,398", "2\"", "1/2\"", "-", "50,80", "12,70", "1,20"],
                    ["1717", "0,395", "1.1/2\"", "1\"", "-", "38,10", "25,40", "1,30"],
                    ["1711", "0,630", "2\"", "1\"", "1/16\"", "50,80", "25,40", "1,58"],
                    ["1723", "0,402", "2\"", "1\"", "-", "50,80", "25,40", "1,00"],
                    ["1714", "0,918", "2\"", "1.1/2\"", "-", "50,80", "38,10", "2,00"],
                    ["TUB4543", "0,800", "-", "1.1/2\"", "-", "60,00", "38,10", "1,20"],
                    ["1716", "0,843", "3\"", "1\"", "1/16\"", "76,20", "25,40", "1,58"],
                    ["1729", "1,780", "3\"", "1.1/2\"", "-", "76,20", "38,10", "3,00"],
                    ["1730", "2,079", "3\"", "2\"", "-", "76,20", "50,80", "3,18"],
                    ["1720", "0,843", "4\"", "1.1/2\"", "-", "101,60", "38,10", "2,50"],
                    ["1722", "1,452", "4\"", "2\"", "-", "101,60", "50,80", "1,80"],
                    ["1727L", "2,613", "6\"", "2\"", "-", "152,80", "50,80", "2,00"],
                    ["1727", "3,206", "6\"", "2\"", "-", "152,80", "50,80", "3,00"],
                ]
            }
        },
        {
            "nome": "Cantoneira de Abas Iguais",
            "tabela": {
                "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada E", "Milímetro A", "Milímetro E"],
                "linhas": [
                    ["1201", "0,100", "1/2\"", "1/16\"", "12,70", "1,60"],
                    ["1205L", "0,076", "5/8\"", "-", "15,87", "0,90"],
                    ["1205", "0,130", "5/8\"", "1/16\"", "15,87", "1,60"],
                    ["1208", "0,150", "3/4\"", "1/16\"", "19,05", "1,60"],
                    ["1208L", "0,090", "3/4\"", "-", "19,05", "0,90"],
                    ["1218", "0,210", "1\"", "1/16\"", "25,40", "1,60"],
                    ["1218L", "0,140", "1\"", "-", "25,40", "0,90"],
                    ["1220", "0,410", "1\"", "1/8\"", "25,40", "3,18"],
                    ["1225", "0,515", "1.1/4\"", "1/8\"", "31,75", "3,18"],
                    ["1230L", "0,318", "1.1/2\"", "1/16\"", "38,10", "1,60"],
                    ["1230", "0,620", "1.1/2\"", "1/8\"", "38,10", "3,18"],
                    ["1231", "0,910", "1.1/2\"", "3/16\"", "38,10", "4,76"],
                    ["1235L", "0,540", "2\"", "-", "50,80", "2,00"],
                    ["1235", "0,840", "2\"", "1/8\"", "50,80", "3,18"],
                    ["1236", "1,233", "2\"", "3/16\"", "50,80", "4,76"],
                ]
            }
        }
    ]
}


DADOS_PAGINA_8 = {
    "pagina": 8,
    "categoria": "Perfis Tabelados",
    "itens": [
        {
            "nome": "Cantoneira de Abas Desiguais",
            "tabela": {
                "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada B", "Polegada E", "Milímetro A", "Milímetro B", "Milímetro E"],
                "linhas": [
                    ["1252L", "0,150", "1\"", "1/2\"", "1/16\"", "25,40", "12,70", "1,60"],
                    ["1252", "0,300", "1\"", "1/2\"", "1/8\"", "25,40", "12,70", "3,18"],
                    ["1261", "0,521", "1.1/2\"", "1\"", "1/8\"", "38,10", "25,40", "3,18"],
                    ["1265", "0,600", "2\"", "1\"", "1/8\"", "50,80", "25,40", "3,18"],
                    ["1267", "0,440", "2\"", "1.1/4\"", "-", "50,80", "38,10", "2,00"],
                ]
            }
        },
        {
            "nome": "Barra Chata",
            "tabela": {
                "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada E", "Milímetro A", "Milímetro E"],
                "linhas": [
                    ["1001", "0,082", "3/8\"", "1/8\"", "9,58", "3,18"],
                    ["1004", "0,108", "1/2\"", "1/8\"", "12,70", "3,18"],
                    ["1011", "0,136", "5/8\"", "1/8\"", "15,87", "3,18"],
                    ["1012", "0,204", "5/8\"", "3/16\"", "15,87", "4,76"],
                    ["1013", "0,272", "5/8\"", "1/4\"", "15,87", "6,35"],
                    ["1014", "0,163", "3/4\"", "1/8\"", "19,05", "3,18"],
                    ["1015", "0,245", "3/4\"", "3/16\"", "19,05", "4,76"],
                    ["1016", "0,327", "3/4\"", "1/4\"", "19,05", "6,35"],
                    ["1021", "0,190", "7/8\"", "1/8\"", "22,22", "3,18"],
                    ["1023", "0,287", "7/8\"", "3/16\"", "22,22", "4,76"],
                    ["1029", "0,218", "1\"", "1/8\"", "25,40", "3,18"],
                    ["1030", "0,326", "1\"", "3/16\"", "25,40", "4,76"],
                    ["1037", "0,272", "1.1/4\"", "1/8\"", "31,75", "3,18"],
                    ["1039", "0,408", "1.1/4\"", "3/16\"", "31,75", "4,76"],
                    ["1082", "0,327", "1.1/2\"", "1/8\"", "38,10", "3,18"],
                    ["1049", "0,490", "1.1/2\"", "3/16\"", "38,10", "4,76"],
                    ["1057", "0,436", "2\"", "1/8\"", "50,80", "3,18"],
                    ["1058", "0,653", "2\"", "3/16\"", "50,80", "4,76"],
                    ["1068", "0,653", "3\"", "1/8\"", "76,20", "3,18"],
                    ["1071", "2,600", "3\"", "1/2\"", "76,20", "12,70"],
                ]
            }
        }
    ]
}


def salvar_dados_extraidos():
    """Salva os dados extraídos manualmente."""
    dados_completos = [DADOS_PAGINA_6, DADOS_PAGINA_7, DADOS_PAGINA_8]

    with open(DADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados_completos, f, indent=2, ensure_ascii=False)

    print("Dados extraídos salvos com sucesso!")
    print(f"Arquivo: {DADOS_FILE}")

    # Mostrar resumo
    for pag in dados_completos:
        print(f"\nPágina {pag['pagina']} - {pag['categoria']}:")
        for item in pag['itens']:
            qtd = len(item['tabela']['linhas'])
            print(f"  - {item['nome']}: {qtd} perfis")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--extrair":
        # Salvar dados extraídos manualmente
        salvar_dados_extraidos()
    else:
        # Executar recortes
        executar_recortes()
        print("\n" + "="*60)
        print("Para salvar os dados extraídos, execute:")
        print("  python extrair_dados.py --extrair")
