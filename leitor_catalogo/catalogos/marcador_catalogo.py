"""
Ferramenta de Marcação Visual do Catálogo - MODO SEMI-AUTOMÁTICO
================================================================
Interface Tkinter para marcar áreas do catálogo com hierarquia:

ITEM (ex: "Tubo Redondo")
  ├── NOME (título na página)
  ├── IMAGEM (desenho técnico)
  └── TABELA (dados do perfil)

Fluxo Semi-Automático:
1. Sugere última categoria usada
2. Pede nome do item
3. Ativa NOME automaticamente -> usuário desenha
4. Ativa IMAGEM automaticamente -> usuário desenha
5. Ativa TABELA automaticamente -> usuário desenha
6. Pergunta se salva -> se sim, próximo item

Trabalha com imagens PNG já extraídas do PDF (mais leve e rápido).
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import json
import glob
import re

# OCR
try:
    import pytesseract
    OCR_DISPONIVEL = True
except ImportError:
    OCR_DISPONIVEL = False

# Configurações
IMAGENS_DIR = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\extracao_conferencia"
MARCACOES_FILE = r"c:\Projects\app_aluminio\leitor_catalogo\catalogos\marcacoes.json"

# Cores para cada tipo de marcação
CORES = {
    "nome": {"cor": "#FF0000", "tag": "NOME"},        # Vermelho
    "imagem": {"cor": "#0066FF", "tag": "IMAGEM"},    # Azul
    "tabela": {"cor": "#00CC00", "tag": "TABELA"},    # Verde
}

# Cor para o item (amarelo/laranja)
COR_ITEM = "#FF9900"

# Sequência de marcações
SEQUENCIA_MARCACAO = ["nome", "imagem", "tabela"]


def fazer_ocr_regiao(imagem, coords):
    """Faz OCR em uma região específica da imagem."""
    if not OCR_DISPONIVEL:
        return ""

    try:
        # Recortar a região
        x1, y1, x2, y2 = [int(c) for c in coords]
        regiao = imagem.crop((x1, y1, x2, y2))

        # Fazer OCR com configuração para português
        texto = pytesseract.image_to_string(
            regiao,
            lang='por',
            config='--psm 6'  # Assume um bloco uniforme de texto
        )

        # Limpar o texto
        texto = texto.strip()
        # Remover quebras de linha e múltiplos espaços
        texto = ' '.join(texto.split())

        return texto
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return ""


class MarcadorCatalogo:
    def __init__(self, root):
        self.root = root
        self.root.title("Marcador de Catálogo - Aluminovo 2025 [MODO SEMI-AUTO]")
        self.root.geometry("1400x900")

        # Estado
        self.imagens = []  # Lista de caminhos das imagens
        self.indice_atual = 0
        self.img_original = None
        self.img_tk = None
        self.tipo_marcacao = tk.StringVar(value="nome")
        self.marcacoes = {}  # {pagina: {"itens": [{"nome": "...", "marcacoes": {...}}]}}
        self.desenho_ativo = False
        self.ponto_inicial = None
        self.retangulo_temp = None

        # Item atual selecionado
        self.item_atual = None  # Nome do item sendo editado

        # Última categoria usada (para sugerir)
        self.ultima_categoria = "Perfis Tabelados"

        # Modo semi-automático
        self.modo_semi_auto = tk.BooleanVar(value=True)
        self.aguardando_marcacao = None  # Qual marcação está esperando

        # Carregar marcações existentes
        self.carregar_marcacoes()

        # Recuperar última categoria das marcações existentes
        self.recuperar_ultima_categoria()

        # Buscar imagens disponíveis
        self.buscar_imagens()

        # Criar interface
        self.criar_interface()

        # Carregar primeira imagem
        if self.imagens:
            self.carregar_imagem(0)

    def recuperar_ultima_categoria(self):
        """Recupera a última categoria usada das marcações existentes."""
        for pag_str in sorted(self.marcacoes.keys(), key=int, reverse=True):
            cat = self.marcacoes[pag_str].get("categoria")
            if cat:
                self.ultima_categoria = cat
                break

    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame superior - controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.pack(fill=tk.X, pady=(0, 5))

        # Navegação de páginas
        nav_frame = ttk.LabelFrame(controles_frame, text="Navegação")
        nav_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(nav_frame, text="◀ Anterior", command=self.pagina_anterior).pack(side=tk.LEFT, padx=2)

        self.lbl_pagina = ttk.Label(nav_frame, text="Página: 1 / ?")
        self.lbl_pagina.pack(side=tk.LEFT, padx=10)

        ttk.Button(nav_frame, text="Próxima ▶", command=self.proxima_pagina).pack(side=tk.LEFT, padx=2)

        ttk.Label(nav_frame, text="  Ir para:").pack(side=tk.LEFT)
        self.entry_pagina = ttk.Entry(nav_frame, width=5)
        self.entry_pagina.pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Ir", command=self.ir_para_pagina).pack(side=tk.LEFT, padx=2)

        # Frame da CATEGORIA
        cat_frame = ttk.LabelFrame(controles_frame, text="Categoria")
        cat_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(cat_frame, text="Mudar", command=self.definir_categoria).pack(side=tk.LEFT, padx=2)
        self.lbl_categoria = ttk.Label(cat_frame, text="(nenhuma)", foreground="gray", width=20)
        self.lbl_categoria.pack(side=tk.LEFT, padx=2)

        # Modo Semi-Auto
        auto_frame = ttk.LabelFrame(controles_frame, text="Modo")
        auto_frame.pack(side=tk.LEFT, padx=5)

        ttk.Checkbutton(auto_frame, text="Semi-Automático", variable=self.modo_semi_auto).pack(side=tk.LEFT, padx=2)

        # Botão INICIAR ITEM (grande e destacado)
        self.btn_iniciar = tk.Button(
            auto_frame,
            text="▶ INICIAR ITEM",
            command=self.iniciar_novo_item,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)

        # Frame do ITEM
        item_frame = ttk.LabelFrame(controles_frame, text="Item Atual")
        item_frame.pack(side=tk.LEFT, padx=5)

        self.lbl_item_atual = ttk.Label(item_frame, text="(nenhum)", foreground="gray", width=18)
        self.lbl_item_atual.pack(side=tk.LEFT, padx=2)

        # Tipo de marcação (indicador visual)
        tipo_frame = ttk.LabelFrame(controles_frame, text="Marcando")
        tipo_frame.pack(side=tk.LEFT, padx=10)

        self.lbl_tipo_atual = tk.Label(
            tipo_frame,
            text="---",
            font=("Arial", 12, "bold"),
            width=10
        )
        self.lbl_tipo_atual.pack(side=tk.LEFT, padx=8)

        # Ações
        acoes_frame = ttk.LabelFrame(controles_frame, text="Ações")
        acoes_frame.pack(side=tk.LEFT, padx=10)

        ttk.Button(acoes_frame, text="Desfazer", command=self.desfazer_ultima).pack(side=tk.LEFT, padx=2)
        ttk.Button(acoes_frame, text="Cancelar Item", command=self.cancelar_item_atual).pack(side=tk.LEFT, padx=2)

        # Frame central com canvas e lista de itens
        centro_frame = ttk.Frame(main_frame)
        centro_frame.pack(fill=tk.BOTH, expand=True)

        # Lista de itens da página (lado esquerdo)
        self.lista_frame = ttk.LabelFrame(centro_frame, text="Itens nesta página")
        self.lista_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        self.lista_itens = tk.Listbox(self.lista_frame, width=30, height=25)
        self.lista_itens.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.lista_itens.bind('<<ListboxSelect>>', self.on_selecionar_item_lista)

        btn_lista_frame = ttk.Frame(self.lista_frame)
        btn_lista_frame.pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(btn_lista_frame, text="Excluir Item", command=self.excluir_item).pack(fill=tk.X)

        # Frame da imagem com scroll
        img_container = ttk.Frame(centro_frame)
        img_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas com scrollbars
        self.canvas = tk.Canvas(img_container, bg="gray", cursor="cross")

        h_scroll = ttk.Scrollbar(img_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(img_container, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Eventos do mouse
        self.canvas.bind("<ButtonPress-1>", self.iniciar_desenho)
        self.canvas.bind("<B1-Motion>", self.desenhar_retangulo)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_desenho)

        # Frame inferior - status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        self.lbl_status = ttk.Label(
            status_frame,
            text="Clique em [▶ INICIAR ITEM] para começar a marcar um novo item.",
            font=("Arial", 11)
        )
        self.lbl_status.pack(side=tk.LEFT)

        self.lbl_marcacoes = ttk.Label(status_frame, text="Itens: 0")
        self.lbl_marcacoes.pack(side=tk.RIGHT)

    def iniciar_novo_item(self):
        """Inicia o fluxo semi-automático para um novo item."""
        # Verificar/definir categoria
        dados = self.get_dados_pagina()
        if not dados.get("categoria"):
            # Sugerir última categoria
            resposta = messagebox.askyesnocancel(
                "Categoria",
                f"Usar categoria: '{self.ultima_categoria}'?\n\n"
                "Sim = Usar esta categoria\n"
                "Não = Digitar outra categoria\n"
                "Cancelar = Cancelar operação"
            )

            if resposta is None:  # Cancelar
                return
            elif resposta:  # Sim
                dados["categoria"] = self.ultima_categoria
            else:  # Não
                nome = simpledialog.askstring(
                    "Categoria da Página",
                    "Nome da categoria:",
                    initialvalue=self.ultima_categoria,
                    parent=self.root
                )
                if not nome or not nome.strip():
                    return
                dados["categoria"] = nome.strip()
                self.ultima_categoria = nome.strip()

            self.lbl_categoria.config(text=dados["categoria"], foreground="black")

        # NÃO pede nome ainda - primeiro desenha o NOME
        # Criar item temporário
        self.item_atual = "__NOVO_ITEM__"
        self.lbl_item_atual.config(text="► (desenhando...)", foreground="orange")

        # Iniciar sequência: ativar NOME primeiro
        self.aguardando_marcacao = "nome"
        self.tipo_marcacao.set("nome")
        self.atualizar_indicador_tipo()

        self.lbl_status.config(text="✏ Desenhe o retângulo do NOME do item (depois você digita o nome)")

    def atualizar_indicador_tipo(self):
        """Atualiza o indicador visual do tipo de marcação atual."""
        tipo = self.aguardando_marcacao
        if tipo:
            cor = CORES[tipo]["cor"]
            tag = CORES[tipo]["tag"]
            self.lbl_tipo_atual.config(text=tag, bg=cor, fg="white")
        else:
            self.lbl_tipo_atual.config(text="---", bg="SystemButtonFace", fg="black")

    def avancar_para_proxima_marcacao(self):
        """Avança para a próxima marcação na sequência."""
        if not self.modo_semi_auto.get() or not self.aguardando_marcacao:
            return

        idx_atual = SEQUENCIA_MARCACAO.index(self.aguardando_marcacao)

        if idx_atual < len(SEQUENCIA_MARCACAO) - 1:
            # Próxima marcação
            proximo = SEQUENCIA_MARCACAO[idx_atual + 1]
            self.aguardando_marcacao = proximo
            self.tipo_marcacao.set(proximo)
            self.atualizar_indicador_tipo()

            tag = CORES[proximo]["tag"]
            self.lbl_status.config(text=f"✏ Agora desenhe o retângulo da {tag} para '{self.item_atual}'")
        else:
            # Finalizou todas as marcações - perguntar se salva
            self.aguardando_marcacao = None
            self.atualizar_indicador_tipo()

            resposta = messagebox.askyesno(
                "Salvar Item",
                f"Item '{self.item_atual}' marcado!\n\nSalvar e iniciar próximo item?"
            )

            if resposta:
                # Salvar
                self.salvar_marcacoes()
                self.lbl_status.config(text=f"✓ Item '{self.item_atual}' salvo! Clique em [▶ INICIAR ITEM] para o próximo.")

                # Resetar para próximo item
                self.item_atual = None
                self.lbl_item_atual.config(text="(nenhum)", foreground="gray")

                # Perguntar se quer iniciar outro
                if messagebox.askyesno("Próximo Item", "Iniciar marcação de outro item?"):
                    self.iniciar_novo_item()
            else:
                self.lbl_status.config(text=f"Item '{self.item_atual}' pronto. Clique em [▶ INICIAR ITEM] para continuar.")

    def cancelar_item_atual(self):
        """Cancela a marcação do item atual."""
        if self.item_atual:
            if messagebox.askyesno("Cancelar", f"Cancelar marcação do item '{self.item_atual}'?"):
                # Remover item incompleto
                itens = self.get_itens_pagina()
                itens[:] = [i for i in itens if i["nome"] != self.item_atual]

                self.item_atual = None
                self.aguardando_marcacao = None
                self.lbl_item_atual.config(text="(nenhum)", foreground="gray")
                self.atualizar_indicador_tipo()
                self.atualizar_lista_itens()
                self.redesenhar_canvas()
                self.lbl_status.config(text="Item cancelado. Clique em [▶ INICIAR ITEM] para começar outro.")

    def buscar_imagens(self):
        """Busca todas as imagens PNG na pasta de extração."""
        padrao = os.path.join(IMAGENS_DIR, "pagina_*_original.png")
        arquivos = glob.glob(padrao)

        def extrair_numero(caminho):
            nome = os.path.basename(caminho)
            match = re.search(r'pagina_(\d+)', nome)
            return int(match.group(1)) if match else 0

        self.imagens = sorted(arquivos, key=extrair_numero)

        if not self.imagens:
            messagebox.showwarning(
                "Aviso",
                f"Nenhuma imagem encontrada em:\n{IMAGENS_DIR}\n\n"
                "Execute primeiro o script de extração de páginas."
            )

    def extrair_pagina_do_nome(self, caminho):
        """Extrai o número da página do nome do arquivo."""
        nome = os.path.basename(caminho)
        match = re.search(r'pagina_(\d+)', nome)
        return int(match.group(1)) if match else 0

    def carregar_imagem(self, indice):
        """Carrega uma imagem específica da lista."""
        if not self.imagens or indice < 0 or indice >= len(self.imagens):
            return

        try:
            caminho = self.imagens[indice]
            self.img_original = Image.open(caminho)
            self.indice_atual = indice

            pagina = self.extrair_pagina_do_nome(caminho)
            total = len(self.imagens)

            self.lbl_pagina.config(text=f"Página {pagina} ({indice + 1}/{total})")

            # Resetar item atual ao mudar de página
            self.item_atual = None
            self.aguardando_marcacao = None
            self.lbl_item_atual.config(text="(nenhum)", foreground="gray")
            self.atualizar_indicador_tipo()

            # Atualizar categoria
            dados = self.get_dados_pagina()
            cat = dados.get("categoria")
            if cat:
                self.lbl_categoria.config(text=cat, foreground="black")
            else:
                self.lbl_categoria.config(text="(nenhuma)", foreground="gray")

            self.redesenhar_canvas()
            self.atualizar_lista_itens()
            self.atualizar_contagem_marcacoes()

            self.lbl_status.config(text="Clique em [▶ INICIAR ITEM] para marcar um novo item.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar imagem:\n{e}")

    def get_pagina_atual(self):
        """Retorna o número da página atual."""
        if self.imagens and 0 <= self.indice_atual < len(self.imagens):
            return self.extrair_pagina_do_nome(self.imagens[self.indice_atual])
        return 0

    def get_dados_pagina(self):
        """Retorna os dados da página atual (cria se não existir)."""
        pag_str = str(self.get_pagina_atual())
        if pag_str not in self.marcacoes:
            self.marcacoes[pag_str] = {"categoria": None, "itens": []}
        return self.marcacoes[pag_str]

    def get_itens_pagina(self):
        """Retorna a lista de itens da página atual."""
        return self.get_dados_pagina()["itens"]

    def definir_categoria(self):
        """Define a categoria da página atual."""
        dados = self.get_dados_pagina()
        atual = dados.get("categoria") or self.ultima_categoria

        nome = simpledialog.askstring(
            "Categoria da Página",
            "Nome da categoria (ex: Perfis Tabelados, Contra Marcos, etc):",
            initialvalue=atual,
            parent=self.root
        )

        if nome is not None:  # Permite string vazia para limpar
            nome = nome.strip() if nome else None
            dados["categoria"] = nome

            if nome:
                self.lbl_categoria.config(text=nome, foreground="black")
                self.lbl_status.config(text=f"Categoria definida: '{nome}'")
                self.ultima_categoria = nome
            else:
                self.lbl_categoria.config(text="(nenhuma)", foreground="gray")
                self.lbl_status.config(text="Categoria removida.")

    def on_selecionar_item_lista(self, event):
        """Callback quando seleciona item na lista."""
        sel = self.lista_itens.curselection()
        if sel:
            itens = self.get_itens_pagina()
            idx = sel[0]
            if idx < len(itens):
                self.item_atual = itens[idx]["nome"]
                self.lbl_item_atual.config(text=f"► {self.item_atual}", foreground="black")
                self.lbl_status.config(text=f"Item '{self.item_atual}' selecionado.")

    def get_status_item(self, item):
        """Retorna string de status do item (quais marcações tem)."""
        marcacoes = item.get("marcacoes", {})
        status = []
        if marcacoes.get("nome"):
            status.append("N")
        if marcacoes.get("imagem"):
            status.append("I")
        if marcacoes.get("tabela"):
            status.append("T")

        if status:
            return f"[{'/'.join(status)}]"
        return "[vazio]"

    def atualizar_lista_itens(self):
        """Atualiza a listbox com os itens da página."""
        self.lista_itens.delete(0, tk.END)

        itens = self.get_itens_pagina()
        for item in itens:
            status = self.get_status_item(item)
            self.lista_itens.insert(tk.END, f"{item['nome']} {status}")

    def excluir_item(self):
        """Exclui o item selecionado na lista."""
        sel = self.lista_itens.curselection()
        if not sel:
            messagebox.showinfo("Info", "Selecione um item na lista para excluir.")
            return

        itens = self.get_itens_pagina()
        idx = sel[0]

        if idx < len(itens):
            nome = itens[idx]["nome"]
            if messagebox.askyesno("Confirmar", f"Excluir item '{nome}' e todas suas marcações?"):
                del itens[idx]

                if self.item_atual == nome:
                    self.item_atual = None
                    self.aguardando_marcacao = None
                    self.lbl_item_atual.config(text="(nenhum)", foreground="gray")
                    self.atualizar_indicador_tipo()

                self.atualizar_lista_itens()
                self.redesenhar_canvas()
                self.atualizar_contagem_marcacoes()
                self.lbl_status.config(text=f"Item '{nome}' excluído.")

    def get_item_por_nome(self, nome):
        """Busca um item pelo nome na página atual."""
        itens = self.get_itens_pagina()
        for item in itens:
            if item["nome"] == nome:
                return item
        return None

    def redesenhar_canvas(self):
        """Redesenha o canvas com a imagem e todas as marcações."""
        if self.img_original is None:
            return

        img_marcada = self.img_original.copy()
        draw = ImageDraw.Draw(img_marcada)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
            font_item = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
            font_item = font

        # Desenhar marcações de todos os itens
        itens = self.get_itens_pagina()

        for item in itens:
            nome_item = item["nome"]
            marcacoes = item.get("marcacoes", {})

            for tipo, coords in marcacoes.items():
                if coords is None:
                    continue

                cor = CORES[tipo]["cor"]
                tag = CORES[tipo]["tag"]

                # Retângulo
                draw.rectangle(coords, outline=cor, width=3)

                # Tag com nome do item
                x1, y1 = coords[0], coords[1]
                texto = f"{nome_item}: {tag}"

                bbox = draw.textbbox((x1, y1 - 22), texto, font=font_item)
                draw.rectangle([bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2], fill=cor)
                draw.text((x1, y1 - 22), texto, fill="white", font=font_item)

        self.img_tk = ImageTk.PhotoImage(img_marcada)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
        self.canvas.configure(scrollregion=(0, 0, img_marcada.width, img_marcada.height))

    def iniciar_desenho(self, event):
        """Inicia o desenho de um retângulo."""
        if self.item_atual is None:
            self.lbl_status.config(text="⚠ Clique em [▶ INICIAR ITEM] primeiro!")
            return

        if self.modo_semi_auto.get() and self.aguardando_marcacao is None and self.item_atual != "__NOVO_ITEM__":
            self.lbl_status.config(text="⚠ Marcação já concluída para este item!")
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.desenho_ativo = True
        self.ponto_inicial = (x, y)

        tipo = self.tipo_marcacao.get()
        cor = CORES[tipo]["cor"]

        self.retangulo_temp = self.canvas.create_rectangle(
            x, y, x, y,
            outline=cor,
            width=2,
            dash=(4, 4)
        )

    def desenhar_retangulo(self, event):
        """Atualiza o retângulo enquanto o mouse se move."""
        if not self.desenho_ativo or self.retangulo_temp is None:
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        x1, y1 = self.ponto_inicial
        self.canvas.coords(self.retangulo_temp, x1, y1, x, y)

    def finalizar_desenho(self, event):
        """Finaliza o desenho e salva a marcação."""
        if not self.desenho_ativo:
            return

        self.desenho_ativo = False

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x1, y1 = self.ponto_inicial

        coords = [min(x1, x), min(y1, y), max(x1, x), max(y1, y)]

        # Verificar tamanho mínimo
        if abs(coords[2] - coords[0]) < 10 or abs(coords[3] - coords[1]) < 10:
            self.canvas.delete(self.retangulo_temp)
            self.retangulo_temp = None
            self.lbl_status.config(text="Retângulo muito pequeno. Tente novamente.")
            return

        self.canvas.delete(self.retangulo_temp)
        self.retangulo_temp = None

        tipo = self.tipo_marcacao.get()

        # Se é o primeiro desenho (NOME) de um novo item, pedir o nome agora
        if self.item_atual == "__NOVO_ITEM__" and tipo == "nome":
            # Salvar coordenadas temporariamente
            self.coords_nome_temp = [int(c) for c in coords]

            # Fazer OCR na região para sugerir o nome
            nome_sugerido = ""
            if OCR_DISPONIVEL and self.img_original:
                self.lbl_status.config(text="Fazendo OCR...")
                self.root.update()
                nome_sugerido = fazer_ocr_regiao(self.img_original, self.coords_nome_temp)

            # Mostrar diálogo com nome sugerido
            if nome_sugerido:
                nome = simpledialog.askstring(
                    "Confirmar Nome do Item",
                    f"OCR detectou: \"{nome_sugerido}\"\n\nConfirme ou corrija o nome:",
                    initialvalue=nome_sugerido,
                    parent=self.root
                )
            else:
                nome = simpledialog.askstring(
                    "Nome do Item",
                    "OCR não conseguiu detectar. Digite o nome do item:",
                    parent=self.root
                )

            if not nome or not nome.strip():
                # Cancelou - limpar
                self.item_atual = None
                self.aguardando_marcacao = None
                self.lbl_item_atual.config(text="(nenhum)", foreground="gray")
                self.atualizar_indicador_tipo()
                self.lbl_status.config(text="Cancelado. Clique em [▶ INICIAR ITEM] para começar.")
                return

            nome = nome.strip()
            itens = self.get_itens_pagina()

            # Verificar se já existe
            for item in itens:
                if item["nome"].lower() == nome.lower():
                    messagebox.showwarning("Aviso", f"Item '{nome}' já existe nesta página.")
                    self.item_atual = None
                    self.aguardando_marcacao = None
                    self.lbl_item_atual.config(text="(nenhum)", foreground="gray")
                    self.atualizar_indicador_tipo()
                    return

            # Criar o item com o nome e as coordenadas do NOME
            novo = {
                "nome": nome,
                "marcacoes": {
                    "nome": self.coords_nome_temp,
                    "imagem": None,
                    "tabela": None
                }
            }
            itens.append(novo)

            self.item_atual = nome
            self.lbl_item_atual.config(text=f"► {nome}", foreground="black")

            self.redesenhar_canvas()
            self.atualizar_lista_itens()
            self.atualizar_contagem_marcacoes()

            self.lbl_status.config(text=f"✓ NOME marcado para '{nome}'!")

            # Avançar para IMAGEM
            if self.modo_semi_auto.get():
                self.root.after(300, self.avancar_para_proxima_marcacao)
            return

        # Fluxo normal para IMAGEM e TABELA
        item = self.get_item_por_nome(self.item_atual)
        if item is None:
            self.lbl_status.config(text="⚠ Item não encontrado!")
            return

        # Salvar marcação no item
        item["marcacoes"][tipo] = [int(c) for c in coords]

        self.redesenhar_canvas()
        self.atualizar_lista_itens()
        self.atualizar_contagem_marcacoes()

        tag = CORES[tipo]["tag"]
        self.lbl_status.config(text=f"✓ {tag} marcado!")

        # Se modo semi-auto, avançar para próxima marcação
        if self.modo_semi_auto.get():
            self.root.after(300, self.avancar_para_proxima_marcacao)

    def desfazer_ultima(self):
        """Remove a última marcação do item atual."""
        if self.item_atual is None:
            self.lbl_status.config(text="Nenhum item selecionado.")
            return

        item = self.get_item_por_nome(self.item_atual)
        if item is None:
            return

        # Remover na ordem inversa: tabela, imagem, nome
        for tipo in ["tabela", "imagem", "nome"]:
            if item["marcacoes"].get(tipo) is not None:
                item["marcacoes"][tipo] = None

                # Voltar para esse tipo no modo semi-auto
                if self.modo_semi_auto.get():
                    self.aguardando_marcacao = tipo
                    self.tipo_marcacao.set(tipo)
                    self.atualizar_indicador_tipo()

                self.redesenhar_canvas()
                self.atualizar_lista_itens()
                self.lbl_status.config(text=f"Marcação {CORES[tipo]['tag']} removida. Desenhe novamente.")
                return

        self.lbl_status.config(text=f"Item '{self.item_atual}' não tem marcações para desfazer.")

    def atualizar_contagem_marcacoes(self):
        """Atualiza o label de contagem de itens."""
        itens = self.get_itens_pagina()
        self.lbl_marcacoes.config(text=f"Itens: {len(itens)}")

    def salvar_marcacoes(self):
        """Salva as marcações em arquivo JSON."""
        try:
            os.makedirs(os.path.dirname(MARCACOES_FILE), exist_ok=True)
            with open(MARCACOES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.marcacoes, f, indent=2, ensure_ascii=False)

            self.lbl_status.config(text=f"Marcações salvas!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{e}")

    def carregar_marcacoes(self):
        """Carrega marcações existentes do arquivo JSON."""
        if os.path.exists(MARCACOES_FILE):
            try:
                with open(MARCACOES_FILE, "r", encoding="utf-8") as f:
                    self.marcacoes = json.load(f)
            except:
                self.marcacoes = {}
        else:
            self.marcacoes = {}

    def pagina_anterior(self):
        """Vai para a imagem anterior."""
        if self.indice_atual > 0:
            self.carregar_imagem(self.indice_atual - 1)

    def proxima_pagina(self):
        """Vai para a próxima imagem."""
        if self.indice_atual < len(self.imagens) - 1:
            self.carregar_imagem(self.indice_atual + 1)

    def ir_para_pagina(self):
        """Vai para a página especificada no entry."""
        try:
            num = int(self.entry_pagina.get())
            for i, caminho in enumerate(self.imagens):
                if self.extrair_pagina_do_nome(caminho) == num:
                    self.carregar_imagem(i)
                    return
            messagebox.showwarning("Aviso", f"Página {num} não encontrada nas imagens extraídas.")
        except ValueError:
            messagebox.showwarning("Aviso", "Digite um número válido")


def main():
    root = tk.Tk()
    app = MarcadorCatalogo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
