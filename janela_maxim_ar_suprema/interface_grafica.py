"""
Interface grafica principal do Visualizador de Janela Maxim-Ar Suprema.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from modelos import DadosJanela
from leitor_excel import ler_excel
from visualizador import VisualizadorJanela


EXCEL_PADRAO = os.path.join(os.path.dirname(__file__), "janela_maxim_ar.xlsx")


class InterfaceVisualizador:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Visualizador Janela Maxim-Ar Suprema")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)

        self.dados: DadosJanela = None
        self.com_contramarco = tk.BooleanVar(value=False)
        self.visualizador = VisualizadorJanela()

        self._resize_timer = None
        self._criar_interface()
        self._carregar_excel()

    def _criar_interface(self):
        # --- Frame superior: info + toggle ---
        frame_topo = ttk.Frame(self.root, padding="6 6 6 4")
        frame_topo.pack(fill='x')

        self.lbl_info = ttk.Label(frame_topo, text="Carregando...",
                                  font=('Arial', 11, 'bold'))
        self.lbl_info.pack(side='left', padx=(0, 30))

        ttk.Label(frame_topo, text="Montagem:",
                  font=('Arial', 10)).pack(side='left', padx=(0, 5))

        ttk.Radiobutton(frame_topo, text="SEM Contramarco",
                        variable=self.com_contramarco, value=False,
                        command=self._redesenhar).pack(side='left', padx=5)
        ttk.Radiobutton(frame_topo, text="COM Contramarco",
                        variable=self.com_contramarco, value=True,
                        command=self._redesenhar).pack(side='left', padx=5)

        ttk.Separator(self.root, orient='horizontal').pack(fill='x')

        # --- Frame central: 3 canvas lado a lado ---
        frame_canvas = ttk.Frame(self.root)
        frame_canvas.pack(fill='both', expand=True, padx=4, pady=4)

        frame_canvas.columnconfigure(0, weight=1)
        frame_canvas.columnconfigure(1, weight=1)
        frame_canvas.columnconfigure(2, weight=1)
        frame_canvas.rowconfigure(0, weight=1)

        # Canvas QUADRO
        frame_q = ttk.LabelFrame(frame_canvas, text=" QUADRO (SU079) ", padding="2")
        frame_q.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        self.canvas_quadro = tk.Canvas(frame_q, bg='#FAFAFA', highlightthickness=0)
        self.canvas_quadro.pack(fill='both', expand=True)

        # Canvas FOLHA
        frame_f = ttk.LabelFrame(frame_canvas, text=" FOLHA (SU082 + SU200) ", padding="2")
        frame_f.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)
        self.canvas_folha = tk.Canvas(frame_f, bg='#FAFAFA', highlightthickness=0)
        self.canvas_folha.pack(fill='both', expand=True)

        # Canvas VIDRO
        frame_v = ttk.LabelFrame(frame_canvas, text=" VIDRO ", padding="2")
        frame_v.grid(row=0, column=2, sticky='nsew', padx=2, pady=2)
        self.canvas_vidro = tk.Canvas(frame_v, bg='#FAFAFA', highlightthickness=0)
        self.canvas_vidro.pack(fill='both', expand=True)

        # Bind resize
        self.canvas_quadro.bind('<Configure>', self._on_resize)
        self.canvas_folha.bind('<Configure>', self._on_resize)
        self.canvas_vidro.bind('<Configure>', self._on_resize)

    def _carregar_excel(self):
        """Carrega o Excel padrao ao iniciar."""
        try:
            self.dados = ler_excel(EXCEL_PADRAO)
            self.lbl_info.config(
                text=f"Vao: {self.dados.largura_vao:.0f} x {self.dados.altura_vao:.0f} mm")
            self.root.after(100, self._redesenhar)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar Excel:\n{e}")
            self.lbl_info.config(text="Erro ao carregar dados")

    def _redesenhar(self):
        """Redesenha os 3 canvas."""
        if not self.dados:
            return
        com = self.com_contramarco.get()
        self.visualizador.desenhar_quadro(self.canvas_quadro, self.dados, com)
        self.visualizador.desenhar_folha(self.canvas_folha, self.dados, com)
        self.visualizador.desenhar_vidro(self.canvas_vidro, self.dados, com)

    def _on_resize(self, event):
        """Redesenha ao redimensionar (com debounce)."""
        if self._resize_timer:
            self.root.after_cancel(self._resize_timer)
        self._resize_timer = self.root.after(150, self._redesenhar)

    def executar(self):
        """Inicia o loop principal do Tkinter."""
        self.root.mainloop()
