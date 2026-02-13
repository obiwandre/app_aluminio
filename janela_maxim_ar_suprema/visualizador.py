"""
Motor de desenho 2D para a Janela Maxim-Ar Suprema.
Desenha as pecas no Canvas do Tkinter com cotas e angulos.
"""
import tkinter as tk
from modelos import DadosJanela, TipoSecao, PosicaoPeca


# Cores dos perfis (referencia do HTML)
CORES = {
    'SU079': '#78909C',
    'SU079_outline': '#546E7A',
    'SU082': '#1565C0',
    'SU200_altura': '#E65100',
    'SU200_largura': '#2E7D32',
    'vidro_fill': '#E1F5FE',
    'vidro_outline': '#90CAF9',
    'angulo_90': '#1565C0',
    'angulo_45': '#C0392B',
    'fundo': '#FAFAFA',
}

# Espessura fixa dos perfis em pixels
ESPESSURA = {
    'SU079': 22,
    'SU082': 18,
    'SU200': 20,
}

# Margens para cotas e legenda
MARGEM_TOPO = 50       # titulo + cota horizontal
MARGEM_ESQUERDA = 65   # cota vertical
MARGEM_DIREITA = 15
MARGEM_INFERIOR_COTA = 30   # espaco para cota inferior
LEGENDA_LINHA_H = 16        # altura de cada linha da legenda


class VisualizadorJanela:
    """Desenha as pecas da janela em um Canvas Tkinter."""

    def _calcular_layout(self, largura_mm, altura_mm, canvas_w, canvas_h, n_legenda):
        """Calcula escala e origem, reservando espaco para legenda embaixo."""
        espaco_legenda = n_legenda * LEGENDA_LINHA_H + 10
        area_x = canvas_w - MARGEM_ESQUERDA - MARGEM_DIREITA
        area_y = canvas_h - MARGEM_TOPO - MARGEM_INFERIOR_COTA - espaco_legenda
        if area_x <= 0 or area_y <= 0:
            return 1.0, MARGEM_ESQUERDA, MARGEM_TOPO, espaco_legenda
        escala = min(area_x / largura_mm, area_y / altura_mm)
        desenho_w = largura_mm * escala
        desenho_h = altura_mm * escala
        ox = MARGEM_ESQUERDA + (area_x - desenho_w) / 2
        oy = MARGEM_TOPO + (area_y - desenho_h) / 2
        return escala, ox, oy, espaco_legenda

    # =====================================================================
    # Utilidades de desenho
    # =====================================================================

    def _desenhar_cota_h(self, canvas, x1, x2, y, valor_mm, label, cor):
        """Desenha cota horizontal com valor e label."""
        canvas.create_line(x1, y, x2, y, fill=cor, width=1.5)
        canvas.create_line(x1, y - 4, x1, y + 4, fill=cor, width=1.5)
        canvas.create_line(x2, y - 4, x2, y + 4, fill=cor, width=1.5)
        mid = (x1 + x2) / 2
        texto = f"{valor_mm:.1f}"
        if label:
            texto += f" ({label})"
        bbox_w = len(texto) * 5.5 + 8
        canvas.create_rectangle(mid - bbox_w / 2, y - 10, mid + bbox_w / 2, y + 3,
                                fill='white', outline='', width=0)
        canvas.create_text(mid, y - 3, text=texto, fill=cor,
                           font=('Arial', 7, 'bold'), anchor='center')

    def _desenhar_cota_v(self, canvas, x, y1, y2, valor_mm, label, cor):
        """Desenha cota vertical com valor acima da linha."""
        canvas.create_line(x, y1, x, y2, fill=cor, width=1.5)
        canvas.create_line(x - 4, y1, x + 4, y1, fill=cor, width=1.5)
        canvas.create_line(x - 4, y2, x + 4, y2, fill=cor, width=1.5)
        mid = (y1 + y2) / 2
        # Valor horizontal ao lado da linha (sem rotacao)
        canvas.create_text(x, mid - 8, text=f"{valor_mm:.1f}",
                           fill=cor, font=('Arial', 7, 'bold'), anchor='center')
        if label:
            canvas.create_text(x, mid + 8, text=label, fill=cor,
                               font=('Arial', 6), anchor='center')

    def _desenhar_angulo(self, canvas, x, y, angulo, cor, canto):
        """Desenha indicador de angulo num canto."""
        tam = 8
        if angulo == 90:
            dx = tam if canto in ('tl', 'bl') else -tam
            dy = tam if canto in ('tl', 'tr') else -tam
            canvas.create_rectangle(x, y, x + dx * 0.6, y + dy * 0.6,
                                    outline=cor, width=1.5)
        elif angulo == 45:
            dx = tam if canto in ('tl', 'bl') else -tam
            dy = tam if canto in ('tl', 'tr') else -tam
            canvas.create_line(x, y + dy, x, y, fill=cor, width=1.5)
            canvas.create_line(x, y, x + dx, y, fill=cor, width=1.5)
            canvas.create_line(x, y, x + dx, y + dy, fill=cor, width=1, dash=(2, 2))

    def _label_perfil(self, canvas, x, y, texto, cor, angulo=0):
        """Desenha label de perfil sobre a peca."""
        canvas.create_text(x, y, text=texto, fill=cor,
                           font=('Arial', 8, 'bold'), anchor='center', angle=angulo)

    def _desenhar_legenda(self, canvas, x_inicio, y_inicio, pecas, com_contramarco):
        """Desenha lista de pecas com medidas abaixo do desenho."""
        y = y_inicio
        for peca in pecas:
            medida = peca.medida(com_contramarco)
            cor = self._cor_perfil(peca)
            # Bolinha colorida
            canvas.create_oval(x_inicio, y - 4, x_inicio + 8, y + 4,
                               fill=cor, outline='')
            # Texto
            texto = f"{peca.perfil} - {peca.posicao.value}: {medida:.1f} mm  ({peca.corte_esq}°/{peca.corte_dir}°)"
            canvas.create_text(x_inicio + 13, y, text=texto, fill='#333',
                               font=('Arial', 8), anchor='w')
            y += LEGENDA_LINHA_H

    def _cor_perfil(self, peca):
        """Retorna a cor de um perfil baseado no tipo."""
        perfil = peca.perfil.upper().replace(" ", "")
        if 'SU079' in perfil or perfil == 'SU079':
            return CORES['SU079']
        elif 'SU082' in perfil or perfil == 'SU082':
            return CORES['SU082']
        elif 'SU200' in perfil or perfil == 'SU200':
            if peca.posicao in (PosicaoPeca.ALTURA_E, PosicaoPeca.ALTURA_D):
                return CORES['SU200_altura']
            return CORES['SU200_largura']
        elif 'VIDRO' in perfil:
            return CORES['vidro_outline']
        return '#666'

    # =====================================================================
    # Desenho do QUADRO (SU079)
    # =====================================================================

    def desenhar_quadro(self, canvas, dados: DadosJanela, com_contramarco: bool):
        """Desenha a secao QUADRO com 4 perfis SU079 formando o marco."""
        canvas.delete("all")
        canvas.configure(bg=CORES['fundo'])

        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 50 or ch < 50:
            return

        q_larg_s = dados.peca_por_posicao(TipoSecao.QUADRO, PosicaoPeca.LARGURA_S)
        q_alt_e = dados.peca_por_posicao(TipoSecao.QUADRO, PosicaoPeca.ALTURA_E)
        larg = q_larg_s.medida(com_contramarco)
        alt = q_alt_e.medida(com_contramarco)

        escala, ox, oy, esp_legenda = self._calcular_layout(
            larg, alt, cw, ch, len(dados.pecas_quadro))
        w = larg * escala
        h = alt * escala
        t = ESPESSURA['SU079']

        cor = CORES['SU079']
        out = CORES['SU079_outline']

        # 4 barras do quadro
        canvas.create_rectangle(ox, oy, ox + w, oy + t, fill=cor, outline=out, width=1)
        self._label_perfil(canvas, ox + w / 2, oy + t / 2, "SU079 - Larg S", 'white')

        canvas.create_rectangle(ox, oy + h - t, ox + w, oy + h, fill=cor, outline=out, width=1)
        self._label_perfil(canvas, ox + w / 2, oy + h - t / 2, "SU079 - Larg I", 'white')

        canvas.create_rectangle(ox, oy, ox + t, oy + h, fill=cor, outline=out, width=1)
        self._label_perfil(canvas, ox + t / 2, oy + h / 2, "Alt E", 'white', angulo=90)

        canvas.create_rectangle(ox + w - t, oy, ox + w, oy + h, fill=cor, outline=out, width=1)
        self._label_perfil(canvas, ox + w - t / 2, oy + h / 2, "Alt D", 'white', angulo=90)

        # Interior
        canvas.create_rectangle(ox + t, oy + t, ox + w - t, oy + h - t,
                                fill='#ECEFF1', outline='#B0BEC5', dash=(4, 4), width=1)

        # Angulos (todos 45°)
        self._desenhar_angulo(canvas, ox, oy, 45, CORES['angulo_45'], 'tl')
        self._desenhar_angulo(canvas, ox + w, oy, 45, CORES['angulo_45'], 'tr')
        self._desenhar_angulo(canvas, ox, oy + h, 45, CORES['angulo_45'], 'bl')
        self._desenhar_angulo(canvas, ox + w, oy + h, 45, CORES['angulo_45'], 'br')

        # Cota horizontal (acima)
        self._desenhar_cota_h(canvas, ox, ox + w, oy - 15,
                              larg, "SU079", cor)
        # Cota vertical (esquerda)
        self._desenhar_cota_v(canvas, ox - 20, oy, oy + h,
                              alt, "SU079", cor)

        # Titulo
        modo = "COM Contramarco" if com_contramarco else "SEM Contramarco"
        canvas.create_text(cw / 2, 10, text=f"QUADRO - {modo}",
                           fill='#37474F', font=('Arial', 10, 'bold'), anchor='center')

        # Legenda embaixo
        legenda_y = oy + h + MARGEM_INFERIOR_COTA
        self._desenhar_legenda(canvas, 10, legenda_y, dados.pecas_quadro, com_contramarco)

    # =====================================================================
    # Desenho da FOLHA (SU082 + SU200)
    # =====================================================================

    def desenhar_folha(self, canvas, dados: DadosJanela, com_contramarco: bool):
        """Desenha a secao FOLHA com SU082 (topo) e SU200 (laterais + inferior)."""
        canvas.delete("all")
        canvas.configure(bg=CORES['fundo'])

        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 50 or ch < 50:
            return

        f_larg_s = dados.peca_por_posicao(TipoSecao.FOLHA, PosicaoPeca.LARGURA_S)  # SU082
        f_larg_i = dados.peca_por_posicao(TipoSecao.FOLHA, PosicaoPeca.LARGURA_I)  # SU200
        f_alt_e = dados.peca_por_posicao(TipoSecao.FOLHA, PosicaoPeca.ALTURA_E)    # SU200

        larg_total = f_larg_i.medida(com_contramarco)
        alt_total = f_alt_e.medida(com_contramarco)

        escala, ox, oy, esp_legenda = self._calcular_layout(
            larg_total, alt_total, cw, ch, len(dados.pecas_folha))
        w = larg_total * escala
        h = alt_total * escala
        t082 = ESPESSURA['SU082']
        t200 = ESPESSURA['SU200']

        # SU200 Altura Esquerda
        canvas.create_rectangle(ox, oy, ox + t200, oy + h,
                                fill=CORES['SU200_altura'], outline='#BF360C', width=1)
        self._label_perfil(canvas, ox + t200 / 2, oy + h / 2, "SU200", 'white', angulo=90)

        # SU200 Altura Direita
        canvas.create_rectangle(ox + w - t200, oy, ox + w, oy + h,
                                fill=CORES['SU200_altura'], outline='#BF360C', width=1)
        self._label_perfil(canvas, ox + w - t200 / 2, oy + h / 2, "SU200", 'white', angulo=90)

        # SU200 Largura Inferior
        canvas.create_rectangle(ox, oy + h - t200, ox + w, oy + h,
                                fill=CORES['SU200_largura'], outline='#1B5E20', width=1)
        self._label_perfil(canvas, ox + w / 2, oy + h - t200 / 2, "SU200 - Larg I", 'white')

        # SU082 Largura Superior (ENTRE os SU200 laterais)
        su082_x1 = ox + t200
        su082_x2 = ox + w - t200
        canvas.create_rectangle(su082_x1, oy, su082_x2, oy + t082,
                                fill=CORES['SU082'], outline='#0D47A1', width=1)
        self._label_perfil(canvas, (su082_x1 + su082_x2) / 2, oy + t082 / 2,
                           "SU082 - Larg S", 'white')

        # Interior (vidro)
        canvas.create_rectangle(ox + t200, oy + t082, ox + w - t200, oy + h - t200,
                                fill='#E1F5FE', outline='#90CAF9', dash=(6, 3), width=1)

        # Angulos
        self._desenhar_angulo(canvas, ox + t200, oy, 90, CORES['angulo_90'], 'tl')
        self._desenhar_angulo(canvas, ox + w - t200, oy, 90, CORES['angulo_90'], 'tr')
        self._desenhar_angulo(canvas, ox, oy + h, 45, CORES['angulo_45'], 'bl')
        self._desenhar_angulo(canvas, ox + w, oy + h, 45, CORES['angulo_45'], 'br')

        # Cota SU082 (acima)
        self._desenhar_cota_h(canvas, su082_x1, su082_x2, oy - 15,
                              f_larg_s.medida(com_contramarco), "SU082", CORES['SU082'])
        # Cota SU200 largura (abaixo)
        self._desenhar_cota_h(canvas, ox, ox + w, oy + h + 15,
                              f_larg_i.medida(com_contramarco), "SU200", CORES['SU200_largura'])
        # Cota SU200 altura (esquerda)
        self._desenhar_cota_v(canvas, ox - 20, oy, oy + h,
                              f_alt_e.medida(com_contramarco), "SU200", CORES['SU200_altura'])

        # Titulo
        modo = "COM Contramarco" if com_contramarco else "SEM Contramarco"
        canvas.create_text(cw / 2, 10, text=f"FOLHA - {modo}",
                           fill='#37474F', font=('Arial', 10, 'bold'), anchor='center')

        # Legenda embaixo
        legenda_y = oy + h + MARGEM_INFERIOR_COTA
        self._desenhar_legenda(canvas, 10, legenda_y, dados.pecas_folha, com_contramarco)

    # =====================================================================
    # Desenho do VIDRO
    # =====================================================================

    def desenhar_vidro(self, canvas, dados: DadosJanela, com_contramarco: bool):
        """Desenha a secao VIDRO como retangulo com dimensoes."""
        canvas.delete("all")
        canvas.configure(bg=CORES['fundo'])

        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 50 or ch < 50:
            return

        v_larg = dados.peca_por_posicao(TipoSecao.VIDRO, PosicaoPeca.LARGURA_S)
        v_alt = dados.peca_por_posicao(TipoSecao.VIDRO, PosicaoPeca.ALTURA_E)
        larg = v_larg.medida(com_contramarco)
        alt = v_alt.medida(com_contramarco)

        # Vidro tem so 2 medidas unicas (largura e altura), mas 4 pecas na lista
        escala, ox, oy, esp_legenda = self._calcular_layout(
            larg, alt, cw, ch, 2)  # so 2 linhas de legenda
        w = larg * escala
        h = alt * escala

        # Retangulo do vidro
        canvas.create_rectangle(ox, oy, ox + w, oy + h,
                                fill=CORES['vidro_fill'], outline=CORES['vidro_outline'],
                                width=2, dash=(8, 4))

        # Diagonais decorativas
        canvas.create_line(ox, oy, ox + w, oy + h,
                           fill=CORES['vidro_outline'], width=0.5, dash=(4, 8))
        canvas.create_line(ox + w, oy, ox, oy + h,
                           fill=CORES['vidro_outline'], width=0.5, dash=(4, 8))

        # Label central
        canvas.create_text(ox + w / 2, oy + h / 2 - 10,
                           text="VIDRO TEMPERADO",
                           fill='#0277BD', font=('Arial', 11, 'bold'), anchor='center')
        canvas.create_text(ox + w / 2, oy + h / 2 + 10,
                           text=f"{larg:.1f} x {alt:.1f} mm",
                           fill='#0277BD', font=('Arial', 9), anchor='center')

        # Cotas
        cor = '#AD1457'
        self._desenhar_cota_h(canvas, ox, ox + w, oy - 15, larg, "Larg", cor)
        self._desenhar_cota_v(canvas, ox - 20, oy, oy + h, alt, "Alt", cor)

        # Titulo
        modo = "COM Contramarco" if com_contramarco else "SEM Contramarco"
        canvas.create_text(cw / 2, 10, text=f"VIDRO - {modo}",
                           fill='#37474F', font=('Arial', 10, 'bold'), anchor='center')

        # Legenda embaixo (so largura e altura, sem repetir)
        legenda_y = oy + h + MARGEM_INFERIOR_COTA
        canvas.create_oval(10, legenda_y - 4, 18, legenda_y + 4,
                           fill=cor, outline='')
        canvas.create_text(23, legenda_y,
                           text=f"Largura: {larg:.1f} mm",
                           fill='#333', font=('Arial', 8), anchor='w')
        legenda_y += LEGENDA_LINHA_H
        canvas.create_oval(10, legenda_y - 4, 18, legenda_y + 4,
                           fill=cor, outline='')
        canvas.create_text(23, legenda_y,
                           text=f"Altura: {alt:.1f} mm",
                           fill='#333', font=('Arial', 8), anchor='w')
