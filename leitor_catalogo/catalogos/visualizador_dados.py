"""
Visualizador de Dados do Catálogo
==================================
Interface Tkinter para visualizar os dados extraídos do catálogo.
"""

import tkinter as tk
from tkinter import ttk
import json
import os
from PIL import Image, ImageTk
import re

# Configurações
DADOS_FILE = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\dados_catalogo.json"
RECORTES_DIR = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\recortes"


class VisualizadorDados:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Dados - Catálogo Aluminovo 2025")
        self.root.geometry("1200x700")

        self.dados = []
        self.carregar_dados()
        self.criar_interface()

    def carregar_dados(self):
        """Carrega os dados do arquivo JSON."""
        if os.path.exists(DADOS_FILE):
            with open(DADOS_FILE, "r", encoding="utf-8") as f:
                self.dados = json.load(f)

    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame esquerdo - navegação
        nav_frame = ttk.LabelFrame(main_frame, text="Navegação")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Treeview para navegação hierárquica
        self.tree = ttk.Treeview(nav_frame, height=30)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.heading("#0", text="Catálogo")
        self.tree.bind("<<TreeviewSelect>>", self.on_selecionar)

        # Scrollbar para treeview
        tree_scroll = ttk.Scrollbar(nav_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        # Preencher treeview
        self.preencher_treeview()

        # Frame direito - detalhes
        detalhe_frame = ttk.LabelFrame(main_frame, text="Dados")
        detalhe_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Info do item selecionado
        self.lbl_info = ttk.Label(detalhe_frame, text="Selecione um item na árvore", font=("Arial", 12, "bold"))
        self.lbl_info.pack(pady=10)

        # Frame para imagem do perfil
        img_frame = ttk.Frame(detalhe_frame)
        img_frame.pack(fill=tk.X, padx=5, pady=5)

        self.lbl_imagem = ttk.Label(img_frame, text="")
        self.lbl_imagem.pack()
        self.img_perfil_tk = None  # Referência para manter a imagem

        # Frame para tabela
        tabela_frame = ttk.Frame(detalhe_frame)
        tabela_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview para mostrar tabela de dados
        self.tabela = ttk.Treeview(tabela_frame, show="headings")
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        scroll_y = ttk.Scrollbar(tabela_frame, orient=tk.VERTICAL, command=self.tabela.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(detalhe_frame, orient=tk.HORIZONTAL, command=self.tabela.xview)
        scroll_x.pack(fill=tk.X)
        self.tabela.configure(xscrollcommand=scroll_x.set)

        # Resumo na parte inferior
        resumo_frame = ttk.LabelFrame(main_frame, text="Resumo")
        resumo_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.lbl_resumo = ttk.Label(resumo_frame, text=self.gerar_resumo())
        self.lbl_resumo.pack(pady=5)

    def preencher_treeview(self):
        """Preenche o treeview com a estrutura dos dados."""
        for pag_dados in self.dados:
            pagina = pag_dados.get("pagina", "?")
            categoria = pag_dados.get("categoria", "Sem categoria")

            # Nó da página
            pag_id = self.tree.insert("", tk.END, text=f"Página {pagina} - {categoria}")

            # Itens da página
            for item in pag_dados.get("itens", []):
                nome = item.get("nome", "?")
                tabela = item.get("tabela", {})
                qtd = len(tabela.get("linhas", []))

                self.tree.insert(pag_id, tk.END, text=f"{nome} ({qtd} perfis)")

    def on_selecionar(self, event):
        """Callback quando seleciona item no treeview."""
        selecionado = self.tree.selection()
        if not selecionado:
            return

        item_id = selecionado[0]
        texto = self.tree.item(item_id, "text")

        # Verificar se é um item (não uma página)
        pai = self.tree.parent(item_id)
        if not pai:
            # É uma página, não um item
            self.lbl_info.config(text=texto)
            self.limpar_tabela()
            return

        # Buscar dados do item
        texto_pai = self.tree.item(pai, "text")
        pagina_str = texto_pai.split(" - ")[0].replace("Página ", "")

        try:
            pagina = int(pagina_str)
        except:
            return

        nome_item = texto.split(" (")[0]

        # Encontrar dados
        for pag_dados in self.dados:
            if pag_dados.get("pagina") == pagina:
                for item in pag_dados.get("itens", []):
                    if item.get("nome") == nome_item:
                        self.mostrar_item(pagina, pag_dados.get("categoria", ""), item)
                        return

    def limpar_tabela(self):
        """Limpa a tabela de dados."""
        for col in self.tabela["columns"]:
            self.tabela.heading(col, text="")
        self.tabela["columns"] = ()
        for item in self.tabela.get_children():
            self.tabela.delete(item)

    def nome_seguro(self, texto):
        """Converte texto para nome de arquivo seguro."""
        return re.sub(r'[^\w\-]', '_', texto)

    def carregar_imagem_perfil(self, pagina, categoria, nome_item):
        """Carrega e exibe a imagem do perfil."""
        # Buscar imagem na pasta de recortes
        pasta = os.path.join(RECORTES_DIR, f"pag{pagina:02d}_{self.nome_seguro(categoria)}")
        arquivo = os.path.join(pasta, f"{self.nome_seguro(nome_item)}_IMAGEM.png")

        if os.path.exists(arquivo):
            try:
                img = Image.open(arquivo)
                # Redimensionar se muito grande
                max_size = (300, 200)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                self.img_perfil_tk = ImageTk.PhotoImage(img)
                self.lbl_imagem.config(image=self.img_perfil_tk, text="")
            except Exception as e:
                self.lbl_imagem.config(image="", text=f"Erro ao carregar imagem: {e}")
                self.img_perfil_tk = None
        else:
            self.lbl_imagem.config(image="", text="(Imagem não disponível)")
            self.img_perfil_tk = None

    def mostrar_item(self, pagina, categoria, item):
        """Mostra os dados de um item na tabela."""
        nome = item.get("nome", "?")
        tabela = item.get("tabela", {})
        cabecalho = tabela.get("cabecalho", [])
        linhas = tabela.get("linhas", [])

        # Atualizar label
        self.lbl_info.config(text=f"{categoria} > {nome} ({len(linhas)} perfis)")

        # Carregar imagem do perfil
        self.carregar_imagem_perfil(pagina, categoria, nome)

        # Limpar tabela
        self.limpar_tabela()

        if not cabecalho:
            return

        # Configurar colunas
        self.tabela["columns"] = tuple(range(len(cabecalho)))

        for i, col in enumerate(cabecalho):
            self.tabela.heading(i, text=col)
            self.tabela.column(i, width=100, anchor=tk.CENTER)

        # Adicionar linhas
        for linha in linhas:
            self.tabela.insert("", tk.END, values=linha)

    def gerar_resumo(self):
        """Gera texto de resumo dos dados."""
        total_paginas = len(self.dados)
        total_itens = 0
        total_perfis = 0

        for pag in self.dados:
            for item in pag.get("itens", []):
                total_itens += 1
                total_perfis += len(item.get("tabela", {}).get("linhas", []))

        return f"Total: {total_paginas} páginas | {total_itens} itens | {total_perfis} perfis"


def main():
    root = tk.Tk()
    app = VisualizadorDados(root)
    root.mainloop()


if __name__ == "__main__":
    main()
