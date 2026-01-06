"""
Otimizador de Corte de Barras de Alumínio
Versão: 0.0.4
Objetivo: Minimizar desperdício e maximizar sobras úteis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Tuple, Dict
from collections import Counter
from datetime import datetime
import csv


class OtimizadorCorte:
    """Classe principal com algoritmos de otimização"""

    def __init__(self, tamanho_barra: float = 600, espessura_corte: float = 0,
                 limite_transporte: float = None):
        self.tamanho_barra = tamanho_barra
        self.espessura_corte = espessura_corte
        self.limite_transporte = limite_transporte  # Ex: 300cm para Spin

    def calcular_cortes_greedy(self, pecas: List[float]) -> List[List[float]]:
        """
        Algoritmo guloso: First Fit Decreasing (FFD)
        Coloca as maiores peças primeiro em cada barra
        """
        pecas_ordenadas = sorted(pecas, reverse=True)
        barras = []

        for peca in pecas_ordenadas:
            colocada = False
            for i, barra in enumerate(barras):
                espaco_usado = sum(barra) + len(barra) * self.espessura_corte
                espaco_necessario = peca + self.espessura_corte
                if espaco_usado + espaco_necessario <= self.tamanho_barra:
                    barras[i].append(peca)
                    colocada = True
                    break

            if not colocada:
                barras.append([peca])

        return barras

    def calcular_cortes_best_fit(self, pecas: List[float]) -> List[List[float]]:
        """
        Best Fit Decreasing: coloca cada peça na barra onde sobra menos espaço
        """
        pecas_ordenadas = sorted(pecas, reverse=True)
        barras = []

        for peca in pecas_ordenadas:
            melhor_barra = -1
            menor_sobra = self.tamanho_barra + 1

            for i, barra in enumerate(barras):
                espaco_usado = sum(barra) + len(barra) * self.espessura_corte
                espaco_necessario = peca + self.espessura_corte
                sobra = self.tamanho_barra - espaco_usado - espaco_necessario
                if sobra >= 0 and sobra < menor_sobra:
                    melhor_barra = i
                    menor_sobra = sobra

            if melhor_barra >= 0:
                barras[melhor_barra].append(peca)
            else:
                barras.append([peca])

        return barras

    def otimizar_para_maiores_sobras(self, pecas: List[float]) -> List[List[float]]:
        """
        Tenta agrupar peças de forma que as sobras sejam as maiores possíveis
        """
        pecas_ordenadas = sorted(pecas, reverse=True)
        barras = []
        pecas_restantes = pecas_ordenadas.copy()

        while pecas_restantes:
            melhor_combo = None
            melhor_uso = 0

            for i, peca in enumerate(pecas_restantes):
                combo = [peca]
                uso = peca + self.espessura_corte
                restantes_temp = pecas_restantes[:i] + pecas_restantes[i+1:]

                for p in restantes_temp:
                    novo_uso = uso + p + self.espessura_corte
                    if novo_uso <= self.tamanho_barra:
                        combo.append(p)
                        uso = novo_uso

                if uso > melhor_uso:
                    melhor_uso = uso
                    melhor_combo = combo

            if melhor_combo:
                barras.append(melhor_combo)
                for p in melhor_combo:
                    pecas_restantes.remove(p)
            else:
                break

        return barras

    def calcular_sobra(self, barra: List[float]) -> float:
        """Calcula sobra considerando espessura do corte"""
        if not barra:
            return self.tamanho_barra
        usado = sum(barra) + len(barra) * self.espessura_corte
        return self.tamanho_barra - usado

    def calcular_corte_transporte(self, barra: List[float]) -> Dict:
        """
        Calcula onde cortar a barra de 600cm para transporte no carro.
        Objetivo: dividir em pedaços <= limite_transporte mantendo a sobra grande.

        Retorna dict com:
        - ponto_corte: onde dar o corte na barra original
        - pedaco_1: lista de peças que ficam no pedaço 1
        - pedaco_2: lista de peças que ficam no pedaço 2
        - tamanho_pedaco_1: tamanho do pedaço 1 após o corte
        - tamanho_pedaco_2: tamanho do pedaço 2 após o corte
        - sobra_fica_em: em qual pedaço fica a sobra
        """
        if not self.limite_transporte:
            return None

        # Ordena peças por tamanho (maior primeiro)
        pecas_ordenadas = sorted(barra, reverse=True)

        # Calcula o uso total e sobra
        uso_total = sum(barra) + len(barra) * self.espessura_corte
        sobra = self.tamanho_barra - uso_total

        # Se tudo cabe no limite, não precisa cortar para transporte
        if uso_total <= self.limite_transporte:
            return {
                'precisa_corte': False,
                'motivo': f'Tudo cabe em {self.limite_transporte}cm',
                'pedaco_unico': uso_total
            }

        # Estratégia: agrupa peças em dois pedaços, tentando:
        # 1. Primeiro: encontrar divisão que cabe no limite
        # 2. Se não encontrar: encontrar a melhor divisão possível (mesmo passando do limite)
        # Em ambos os casos, maximiza a sobra em um dos pedaços

        melhor_divisao_dentro_limite = None
        melhor_divisao_geral = None
        melhor_score_limite = -1  # Score para divisões dentro do limite
        melhor_score_geral = float('inf')  # Score para melhor divisão geral (menor excesso)

        # Gera todas as possíveis divisões das peças em dois grupos
        n = len(pecas_ordenadas)

        for mask in range(1, 2**n):  # Todas combinações exceto vazio
            grupo1 = []
            grupo2 = []

            for i in range(n):
                if mask & (1 << i):
                    grupo1.append(pecas_ordenadas[i])
                else:
                    grupo2.append(pecas_ordenadas[i])

            if not grupo1 or not grupo2:
                continue

            # Calcula tamanho de cada pedaço (peças + cortes entre elas)
            tam_grupo1 = sum(grupo1) + len(grupo1) * self.espessura_corte
            tam_grupo2 = sum(grupo2) + len(grupo2) * self.espessura_corte

            # Testa as duas opções de onde colocar a sobra
            for sobra_em in [1, 2]:
                if sobra_em == 1:
                    tam_pedaco1 = tam_grupo1 + sobra
                    tam_pedaco2 = tam_grupo2 + self.espessura_corte
                    ponto = tam_grupo2 + self.espessura_corte
                else:
                    tam_pedaco1 = tam_grupo1 + self.espessura_corte
                    tam_pedaco2 = tam_grupo2 + sobra
                    ponto = tam_grupo1 + self.espessura_corte

                # Calcula o maior pedaço (o que importa pro transporte)
                maior_pedaco = max(tam_pedaco1, tam_pedaco2)
                excesso = max(0, maior_pedaco - self.limite_transporte)

                divisao = {
                    'precisa_corte': True,
                    'pedaco_1': grupo1.copy(),
                    'pedaco_2': grupo2.copy(),
                    'tamanho_pedaco_1': tam_pedaco1,
                    'tamanho_pedaco_2': tam_pedaco2,
                    'sobra_fica_em': sobra_em,
                    'sobra': sobra,
                    'ponto_corte': ponto,
                    'excesso': excesso
                }

                # Se cabe no limite, guarda como melhor dentro do limite
                if tam_pedaco1 <= self.limite_transporte and tam_pedaco2 <= self.limite_transporte:
                    if sobra > melhor_score_limite:
                        melhor_score_limite = sobra
                        melhor_divisao_dentro_limite = divisao.copy()
                        melhor_divisao_dentro_limite['cabe_no_limite'] = True

                # Guarda a melhor divisão geral (menor excesso, depois maior sobra)
                # Score: (excesso, -sobra) - menor excesso é melhor, depois maior sobra
                score_atual = (excesso, -sobra)
                score_melhor = (melhor_score_geral, float('inf'))
                if melhor_divisao_geral:
                    score_melhor = (melhor_divisao_geral.get('excesso', float('inf')), -melhor_divisao_geral.get('sobra', 0))

                if score_atual < score_melhor:
                    melhor_score_geral = excesso
                    melhor_divisao_geral = divisao.copy()
                    melhor_divisao_geral['cabe_no_limite'] = (excesso == 0)

        # Retorna a divisão dentro do limite se existir, senão a melhor geral
        if melhor_divisao_dentro_limite:
            return melhor_divisao_dentro_limite

        if melhor_divisao_geral:
            return melhor_divisao_geral

        # Fallback: corte no meio (não deveria chegar aqui)
        return {
            'precisa_corte': True,
            'ponto_corte': self.tamanho_barra / 2,
            'tamanho_pedaco_1': self.tamanho_barra / 2,
            'tamanho_pedaco_2': self.tamanho_barra / 2 - self.espessura_corte,
            'excesso': max(0, self.tamanho_barra / 2 - self.limite_transporte),
            'cabe_no_limite': False
        }

    def analisar_resultado(self, barras: List[List[float]]) -> dict:
        """Retorna análise completa do resultado"""
        sobras = [self.calcular_sobra(b) for b in barras]
        material_usado = sum(sum(b) for b in barras)
        material_total = len(barras) * self.tamanho_barra

        # Calcula cortes de transporte se limite definido
        cortes_transporte = []
        if self.limite_transporte:
            for barra in barras:
                corte = self.calcular_corte_transporte(barra)
                cortes_transporte.append(corte)

        return {
            'barras': barras,
            'num_barras': len(barras),
            'sobras': sobras,
            'sobra_total': sum(sobras),
            'material_usado': material_usado,
            'material_total': material_total,
            'eficiencia': (material_usado / material_total * 100) if material_total > 0 else 0,
            'cortes_transporte': cortes_transporte if cortes_transporte else None
        }


class InterfaceGrafica:
    """Interface gráfica com Tkinter"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Otimizador de Corte de Barras de Alumínio v0.0.3")
        self.root.geometry("950x750")
        self.root.minsize(900, 700)

        self.pecas = []
        self.ultimo_resultado = None

        self.criar_interface()

    def criar_interface(self):
        # Frame principal com scroll
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

        # === Configurações ===
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(config_frame, text="Tamanho da barra (cm):").grid(row=0, column=0, padx=5)
        self.entry_tamanho = ttk.Entry(config_frame, width=10)
        self.entry_tamanho.insert(0, "600")
        self.entry_tamanho.grid(row=0, column=1, padx=5)

        ttk.Label(config_frame, text="Espessura do corte (mm):").grid(row=0, column=2, padx=5)
        self.entry_espessura = ttk.Entry(config_frame, width=10)
        self.entry_espessura.insert(0, "3")
        self.entry_espessura.grid(row=0, column=3, padx=5)

        # === Transporte ===
        transporte_frame = ttk.LabelFrame(main_frame, text="Corte para Transporte (opcional)", padding="10")
        transporte_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.var_transporte = tk.BooleanVar(value=False)
        ttk.Checkbutton(transporte_frame, text="Calcular corte para transporte",
                        variable=self.var_transporte, command=self.toggle_transporte).grid(row=0, column=0, padx=5)

        ttk.Label(transporte_frame, text="Limite do carro (cm):").grid(row=0, column=1, padx=5)
        self.entry_limite = ttk.Entry(transporte_frame, width=10)
        self.entry_limite.insert(0, "300")
        self.entry_limite.config(state='disabled')
        self.entry_limite.grid(row=0, column=2, padx=5)

        ttk.Label(transporte_frame, text="(Ex: Spin = 300cm)").grid(row=0, column=3, padx=5)

        # === Entrada de peças ===
        input_frame = ttk.LabelFrame(main_frame, text="Adicionar Peças", padding="10")
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(input_frame, text="Medida (cm):").grid(row=0, column=0, padx=5)
        self.entry_medida = ttk.Entry(input_frame, width=10)
        self.entry_medida.grid(row=0, column=1, padx=5)
        self.entry_medida.bind('<Return>', lambda e: self.adicionar_peca())

        ttk.Label(input_frame, text="Quantidade:").grid(row=0, column=2, padx=5)
        self.entry_quantidade = ttk.Entry(input_frame, width=10)
        self.entry_quantidade.insert(0, "1")
        self.entry_quantidade.grid(row=0, column=3, padx=5)
        self.entry_quantidade.bind('<Return>', lambda e: self.adicionar_peca())

        ttk.Button(input_frame, text="Adicionar", command=self.adicionar_peca).grid(row=0, column=4, padx=5)
        ttk.Button(input_frame, text="Limpar Tudo", command=self.limpar_pecas).grid(row=0, column=5, padx=5)

        # === Quadros pré-definidos ===
        quadro_frame = ttk.LabelFrame(main_frame, text="Adicionar Quadro (4 lados)", padding="10")
        quadro_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(quadro_frame, text="Medidas do quadro (ex: 75x75x40x40):").grid(row=0, column=0, padx=5)
        self.entry_quadro = ttk.Entry(quadro_frame, width=20)
        self.entry_quadro.grid(row=0, column=1, padx=5)
        self.entry_quadro.bind('<Return>', lambda e: self.adicionar_quadro())

        ttk.Button(quadro_frame, text="Adicionar Quadro", command=self.adicionar_quadro).grid(row=0, column=2, padx=5)

        # === Lista de peças ===
        lista_frame = ttk.LabelFrame(main_frame, text="Peças Adicionadas", padding="10")
        lista_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10), padx=(0, 5))
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        self.lista_pecas = tk.Listbox(lista_frame, width=30, height=8)
        self.lista_pecas.grid(row=0, column=0, sticky="nsew")

        scrollbar_lista = ttk.Scrollbar(lista_frame, orient="vertical", command=self.lista_pecas.yview)
        scrollbar_lista.grid(row=0, column=1, sticky="ns")
        self.lista_pecas.config(yscrollcommand=scrollbar_lista.set)

        ttk.Button(lista_frame, text="Remover Selecionada", command=self.remover_peca).grid(row=1, column=0, pady=5)

        # === Botão calcular ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=1, sticky="n", pady=(0, 10))

        ttk.Button(btn_frame, text="CALCULAR OTIMIZAÇÃO", command=self.calcular,
                   style="Accent.TButton").grid(row=0, column=0, pady=10, ipady=10, ipadx=20)

        ttk.Button(btn_frame, text="Salvar Resultado (TXT)", command=self.salvar_txt).grid(row=1, column=0, pady=5)
        ttk.Button(btn_frame, text="Salvar Resultado (CSV)", command=self.salvar_csv).grid(row=2, column=0, pady=5)

        # === Resultado ===
        resultado_frame = ttk.LabelFrame(main_frame, text="Resultado da Otimização", padding="10")
        resultado_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")
        resultado_frame.columnconfigure(0, weight=1)
        resultado_frame.rowconfigure(0, weight=1)

        self.texto_resultado = tk.Text(resultado_frame, wrap=tk.WORD, width=80, height=18, font=('Consolas', 10))
        self.texto_resultado.grid(row=0, column=0, sticky="nsew")

        scrollbar_resultado = ttk.Scrollbar(resultado_frame, orient="vertical", command=self.texto_resultado.yview)
        scrollbar_resultado.grid(row=0, column=1, sticky="ns")
        self.texto_resultado.config(yscrollcommand=scrollbar_resultado.set)

        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(5, weight=2)

    def toggle_transporte(self):
        if self.var_transporte.get():
            self.entry_limite.config(state='normal')
        else:
            self.entry_limite.config(state='disabled')

    def adicionar_peca(self):
        try:
            medida = float(self.entry_medida.get().replace(',', '.'))
            quantidade = int(self.entry_quantidade.get())

            if medida <= 0:
                messagebox.showerror("Erro", "A medida deve ser maior que zero!")
                return

            if quantidade <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero!")
                return

            for _ in range(quantidade):
                self.pecas.append(medida)

            self.atualizar_lista_pecas()
            self.entry_medida.delete(0, tk.END)
            self.entry_quantidade.delete(0, tk.END)
            self.entry_quantidade.insert(0, "1")
            self.entry_medida.focus()

        except ValueError:
            messagebox.showerror("Erro", "Digite valores numéricos válidos!")

    def adicionar_quadro(self):
        try:
            texto = self.entry_quadro.get().strip()
            medidas = [float(m.replace(',', '.')) for m in texto.lower().replace('x', ' ').split()]

            if len(medidas) != 4:
                messagebox.showerror("Erro", "Digite 4 medidas separadas por 'x' (ex: 75x75x40x40)")
                return

            for medida in medidas:
                if medida <= 0:
                    messagebox.showerror("Erro", "Todas as medidas devem ser maiores que zero!")
                    return
                self.pecas.append(medida)

            self.atualizar_lista_pecas()
            self.entry_quadro.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Erro", "Formato inválido! Use: 75x75x40x40")

    def remover_peca(self):
        selecao = self.lista_pecas.curselection()
        if selecao:
            texto = self.lista_pecas.get(selecao[0])
            if "cm x" in texto:
                medida = float(texto.split('cm')[0].strip())
                if medida in self.pecas:
                    self.pecas.remove(medida)
                self.atualizar_lista_pecas()

    def limpar_pecas(self):
        self.pecas = []
        self.atualizar_lista_pecas()
        self.texto_resultado.delete(1.0, tk.END)

    def atualizar_lista_pecas(self):
        self.lista_pecas.delete(0, tk.END)
        contagem = Counter(self.pecas)
        for medida, qtd in sorted(contagem.items(), reverse=True):
            self.lista_pecas.insert(tk.END, f"{medida}cm x {qtd}")

        total = sum(self.pecas)
        self.lista_pecas.insert(tk.END, "─" * 20)
        self.lista_pecas.insert(tk.END, f"Total: {total}cm ({len(self.pecas)} peças)")

    def calcular(self):
        if not self.pecas:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma peça!")
            return

        try:
            tamanho_barra = float(self.entry_tamanho.get().replace(',', '.'))
            espessura_mm = float(self.entry_espessura.get().replace(',', '.'))
            espessura_cm = espessura_mm / 10

            limite_transporte = None
            if self.var_transporte.get():
                limite_transporte = float(self.entry_limite.get().replace(',', '.'))

        except ValueError:
            messagebox.showerror("Erro", "Configurações inválidas!")
            return

        # Verifica se alguma peça é maior que a barra
        for peca in self.pecas:
            if peca > tamanho_barra:
                messagebox.showerror("Erro", f"Peça de {peca}cm é maior que a barra de {tamanho_barra}cm!")
                return

        # Verifica se alguma peça é maior que o limite de transporte
        if limite_transporte:
            for peca in self.pecas:
                if peca > limite_transporte:
                    messagebox.showwarning("Aviso",
                        f"Peça de {peca}cm é maior que o limite de transporte ({limite_transporte}cm).\n"
                        "Você precisará de um veículo maior para esta peça.")

        otimizador = OtimizadorCorte(tamanho_barra, espessura_cm, limite_transporte)

        # Calcula com os 3 métodos
        resultado_ffd = otimizador.analisar_resultado(otimizador.calcular_cortes_greedy(self.pecas))
        resultado_bfd = otimizador.analisar_resultado(otimizador.calcular_cortes_best_fit(self.pecas))
        resultado_otim = otimizador.analisar_resultado(otimizador.otimizar_para_maiores_sobras(self.pecas))

        resultados = [
            ('First Fit Decreasing', resultado_ffd),
            ('Best Fit Decreasing', resultado_bfd),
            ('Otimizado p/ Maiores Sobras', resultado_otim)
        ]

        melhor_nome, melhor = min(resultados, key=lambda x: (x[1]['num_barras'], -max(x[1]['sobras'])))

        self.ultimo_resultado = {
            'tamanho_barra': tamanho_barra,
            'espessura_corte': espessura_mm,
            'limite_transporte': limite_transporte,
            'pecas': self.pecas.copy(),
            'metodo': melhor_nome,
            'resultado': melhor
        }

        # Exibe resultado
        self.texto_resultado.delete(1.0, tk.END)

        texto = "=" * 65 + "\n"
        texto += "RESULTADO DA OTIMIZAÇÃO\n"
        texto += "=" * 65 + "\n\n"

        texto += f"Configurações:\n"
        texto += f"  • Tamanho da barra: {tamanho_barra}cm\n"
        texto += f"  • Espessura do corte: {espessura_mm}mm\n"
        if limite_transporte:
            texto += f"  • Limite transporte: {limite_transporte}cm\n"
        texto += f"  • Total de peças: {len(self.pecas)}\n"
        texto += f"  • Método usado: {melhor_nome}\n\n"

        texto += "-" * 65 + "\n"
        texto += f">>> VOCÊ PRECISARÁ DE {melhor['num_barras']} BARRA(S) DE {tamanho_barra}cm <<<\n"
        texto += "-" * 65 + "\n\n"

        texto += "PLANO DE CORTE:\n"
        texto += "=" * 65 + "\n"

        for i, barra in enumerate(melhor['barras'], 1):
            sobra = otimizador.calcular_sobra(barra)
            pecas_str = " + ".join(f"{p}cm" for p in sorted(barra, reverse=True))

            texto += f"\n📦 BARRA {i}:\n"
            texto += f"   Peças: {pecas_str}\n"
            texto += f"   Usado: {sum(barra):.1f}cm | Sobra: {sobra:.1f}cm\n"

            # Mostra corte de transporte se habilitado
            if melhor['cortes_transporte'] and melhor['cortes_transporte'][i-1]:
                corte = melhor['cortes_transporte'][i-1]

                if not corte.get('precisa_corte', True):
                    texto += f"\n   🚗 TRANSPORTE: Cabe inteira no carro ({corte.get('pedaco_unico', 0):.1f}cm)\n"
                else:
                    texto += f"\n   🚗 CORTE PARA TRANSPORTE (limite {limite_transporte}cm):\n"

                    # Aviso se passa do limite
                    if not corte.get('cabe_no_limite', True) and corte.get('excesso', 0) > 0:
                        texto += f"   ⚠️  ATENÇÃO: Passa {corte['excesso']:.1f}cm do limite!\n"

                    texto += f"   ✂️  Cortar em: {corte['ponto_corte']:.1f}cm da ponta\n"

                    texto += f"\n   Pedaço A ({corte['tamanho_pedaco_1']:.1f}cm)"
                    if corte['tamanho_pedaco_1'] > limite_transporte:
                        texto += f" ⚠️ +{corte['tamanho_pedaco_1'] - limite_transporte:.1f}cm"
                    texto += ":\n"
                    if 'pedaco_1' in corte:
                        texto += f"      Peças: {' + '.join(f'{p}cm' for p in sorted(corte['pedaco_1'], reverse=True))}\n"
                        if corte.get('sobra_fica_em') == 1 and corte.get('sobra', 0) > 0:
                            texto += f"      + Sobra de {corte['sobra']:.1f}cm\n"

                    texto += f"\n   Pedaço B ({corte['tamanho_pedaco_2']:.1f}cm)"
                    if corte['tamanho_pedaco_2'] > limite_transporte:
                        texto += f" ⚠️ +{corte['tamanho_pedaco_2'] - limite_transporte:.1f}cm"
                    texto += ":\n"
                    if 'pedaco_2' in corte:
                        texto += f"      Peças: {' + '.join(f'{p}cm' for p in sorted(corte['pedaco_2'], reverse=True))}\n"
                        if corte.get('sobra_fica_em') == 2 and corte.get('sobra', 0) > 0:
                            texto += f"      + Sobra de {corte['sobra']:.1f}cm\n"

            texto += "\n" + "-" * 65 + "\n"

        texto += "\nRESUMO:\n"
        texto += f"  • Material total: {melhor['material_total']:.1f}cm\n"
        texto += f"  • Material usado: {melhor['material_usado']:.1f}cm\n"
        texto += f"  • Sobra total: {melhor['sobra_total']:.1f}cm\n"
        texto += f"  • Eficiência: {melhor['eficiencia']:.1f}%\n"
        texto += f"  • Sobras por barra: {[f'{s:.1f}cm' for s in sorted(melhor['sobras'], reverse=True)]}\n"

        self.texto_resultado.insert(1.0, texto)

    def salvar_txt(self):
        if not self.ultimo_resultado:
            messagebox.showwarning("Aviso", "Calcule a otimização primeiro!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt")],
            initialfilename=f"corte_aluminio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.texto_resultado.get(1.0, tk.END))
            messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{filepath}")

    def salvar_csv(self):
        if not self.ultimo_resultado:
            messagebox.showwarning("Aviso", "Calcule a otimização primeiro!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            initialfilename=f"corte_aluminio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if filepath:
            resultado = self.ultimo_resultado
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')

                writer.writerow(['OTIMIZADOR DE CORTE DE BARRAS DE ALUMÍNIO v0.0.3'])
                writer.writerow(['Data', datetime.now().strftime('%d/%m/%Y %H:%M')])
                writer.writerow(['Tamanho da Barra (cm)', resultado['tamanho_barra']])
                writer.writerow(['Espessura do Corte (mm)', resultado['espessura_corte']])
                if resultado.get('limite_transporte'):
                    writer.writerow(['Limite Transporte (cm)', resultado['limite_transporte']])
                writer.writerow(['Método', resultado['metodo']])
                writer.writerow([])

                writer.writerow(['PEÇAS NECESSÁRIAS'])
                writer.writerow(['Medida (cm)', 'Quantidade'])
                contagem = Counter(resultado['pecas'])
                for medida, qtd in sorted(contagem.items(), reverse=True):
                    writer.writerow([medida, qtd])
                writer.writerow([])

                writer.writerow(['PLANO DE CORTE'])
                writer.writerow(['Barra', 'Peças (cm)', 'Total Usado (cm)', 'Sobra (cm)', 'Corte Transporte (cm)'])

                otimizador = OtimizadorCorte(resultado['tamanho_barra'], resultado['espessura_corte']/10,
                                             resultado.get('limite_transporte'))

                for i, barra in enumerate(resultado['resultado']['barras'], 1):
                    pecas_str = ' + '.join(str(p) for p in sorted(barra, reverse=True))
                    sobra = otimizador.calcular_sobra(barra)

                    corte_str = '-'
                    if resultado['resultado'].get('cortes_transporte'):
                        corte = resultado['resultado']['cortes_transporte'][i-1]
                        if corte and corte.get('precisa_corte'):
                            corte_str = f"{corte.get('ponto_corte', 'N/A')}"

                    writer.writerow([i, pecas_str, sum(barra), f'{sobra:.1f}', corte_str])

                writer.writerow([])
                writer.writerow(['RESUMO'])
                writer.writerow(['Total de Barras', resultado['resultado']['num_barras']])
                writer.writerow(['Eficiência', f"{resultado['resultado']['eficiencia']:.1f}%"])

            messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{filepath}")

    def executar(self):
        self.root.mainloop()


def modo_terminal():
    """Modo interativo via terminal"""
    print("=" * 65)
    print("OTIMIZADOR DE CORTE DE BARRAS DE ALUMÍNIO v0.0.3")
    print("=" * 65)

    # Configurações
    tamanho_input = input("\nTamanho da barra em cm [600]: ").strip()
    tamanho_barra = float(tamanho_input) if tamanho_input else 600

    espessura_input = input("Espessura do corte em mm [3]: ").strip()
    espessura_mm = float(espessura_input) if espessura_input else 3
    espessura_cm = espessura_mm / 10

    transporte_input = input("Limite do carro em cm (Enter para ignorar) [300]: ").strip()
    limite_transporte = float(transporte_input) if transporte_input else None

    pecas = []

    print("\n--- Adicionar Peças ---")
    print("Digite as medidas em cm (ou 'q' para calcular)")
    print("Formato: medida ou medidaxquantidade (ex: 75 ou 75x4)")
    print("Para quadros: 75x75x40x40 (4 medidas)\n")

    while True:
        entrada = input("Peça: ").strip().lower()

        if entrada == 'q' or entrada == '':
            if pecas:
                break
            print("Adicione pelo menos uma peça!")
            continue

        try:
            partes = entrada.replace(',', '.').split('x')

            if len(partes) == 1:
                pecas.append(float(partes[0]))
            elif len(partes) == 2:
                medida = float(partes[0])
                qtd = int(partes[1])
                pecas.extend([medida] * qtd)
            elif len(partes) == 4:
                for p in partes:
                    pecas.append(float(p))
            else:
                print("Formato inválido!")
                continue

            print(f"  Adicionado! Total: {len(pecas)} peças ({sum(pecas)}cm)")

        except ValueError:
            print("Valor inválido!")

    otimizador = OtimizadorCorte(tamanho_barra, espessura_cm, limite_transporte)

    resultado_ffd = otimizador.analisar_resultado(otimizador.calcular_cortes_greedy(pecas))
    resultado_bfd = otimizador.analisar_resultado(otimizador.calcular_cortes_best_fit(pecas))
    resultado_otim = otimizador.analisar_resultado(otimizador.otimizar_para_maiores_sobras(pecas))

    resultados = [
        ('First Fit Decreasing', resultado_ffd),
        ('Best Fit Decreasing', resultado_bfd),
        ('Otimizado p/ Maiores Sobras', resultado_otim)
    ]

    melhor_nome, melhor = min(resultados, key=lambda x: (x[1]['num_barras'], -max(x[1]['sobras'])))

    print("\n" + "=" * 65)
    print("RESULTADO DA OTIMIZAÇÃO")
    print("=" * 65)

    print(f"\nConfiguração: Barra {tamanho_barra}cm, Corte {espessura_mm}mm")
    if limite_transporte:
        print(f"Limite transporte: {limite_transporte}cm")
    print(f"Método: {melhor_nome}")

    print("\n" + "-" * 65)
    print(f">>> VOCÊ PRECISARÁ DE {melhor['num_barras']} BARRA(S) <<<")
    print("-" * 65)

    print("\nPLANO DE CORTE:\n")

    for i, barra in enumerate(melhor['barras'], 1):
        sobra = otimizador.calcular_sobra(barra)
        pecas_str = " + ".join(f"{p}cm" for p in sorted(barra, reverse=True))
        print(f"BARRA {i}: {pecas_str}")
        print(f"         Usado: {sum(barra):.1f}cm | Sobra: {sobra:.1f}cm")

        if melhor['cortes_transporte'] and melhor['cortes_transporte'][i-1]:
            corte = melhor['cortes_transporte'][i-1]
            if not corte.get('precisa_corte', True):
                print(f"         Transporte: Cabe inteira no carro")
            elif 'ponto_corte' in corte:
                if not corte.get('cabe_no_limite', True) and corte.get('excesso', 0) > 0:
                    print(f"         ⚠️  ATENÇÃO: Passa {corte['excesso']:.1f}cm do limite!")
                print(f"         Corte transporte: {corte['ponto_corte']:.1f}cm da ponta")
                if 'pedaco_1' in corte:
                    extra_a = f" (+{corte['tamanho_pedaco_1'] - limite_transporte:.1f}cm)" if corte['tamanho_pedaco_1'] > limite_transporte else ""
                    extra_b = f" (+{corte['tamanho_pedaco_2'] - limite_transporte:.1f}cm)" if corte['tamanho_pedaco_2'] > limite_transporte else ""
                    print(f"           Pedaço A ({corte['tamanho_pedaco_1']:.1f}cm){extra_a}: {' + '.join(f'{p}cm' for p in corte['pedaco_1'])}")
                    print(f"           Pedaço B ({corte['tamanho_pedaco_2']:.1f}cm){extra_b}: {' + '.join(f'{p}cm' for p in corte['pedaco_2'])}")
        print()

    print("-" * 65)
    print(f"Eficiência: {melhor['eficiencia']:.1f}%")
    print(f"Sobras: {[f'{s:.1f}cm' for s in sorted(melhor['sobras'], reverse=True)]}")

    salvar = input("\nSalvar resultado? (txt/csv/n): ").strip().lower()

    if salvar == 'txt':
        nome = f"corte_aluminio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(nome, 'w', encoding='utf-8') as f:
            f.write(f"OTIMIZADOR DE CORTE v0.0.3 - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Barra: {tamanho_barra}cm | Corte: {espessura_mm}mm")
            if limite_transporte:
                f.write(f" | Transporte: {limite_transporte}cm")
            f.write(f"\nBarras necessárias: {melhor['num_barras']}\n\n")
            for i, barra in enumerate(melhor['barras'], 1):
                sobra = otimizador.calcular_sobra(barra)
                f.write(f"Barra {i}: {' + '.join(f'{p}cm' for p in sorted(barra, reverse=True))}\n")
                f.write(f"         Sobra: {sobra:.1f}cm\n")
                if melhor['cortes_transporte'] and melhor['cortes_transporte'][i-1]:
                    corte = melhor['cortes_transporte'][i-1]
                    if corte.get('precisa_corte') and 'ponto_corte' in corte:
                        f.write(f"         Corte transporte: {corte['ponto_corte']:.1f}cm\n")
                f.write("\n")
        print(f"Salvo em: {nome}")

    elif salvar == 'csv':
        nome = f"corte_aluminio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(nome, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Barra', 'Peças', 'Sobra (cm)', 'Corte Transporte (cm)'])
            for i, barra in enumerate(melhor['barras'], 1):
                sobra = otimizador.calcular_sobra(barra)
                corte_str = '-'
                if melhor['cortes_transporte'] and melhor['cortes_transporte'][i-1]:
                    corte = melhor['cortes_transporte'][i-1]
                    if corte.get('precisa_corte') and 'ponto_corte' in corte:
                        corte_str = f"{corte['ponto_corte']:.1f}"
                writer.writerow([i, ' + '.join(str(p) for p in barra), f'{sobra:.1f}', corte_str])
        print(f"Salvo em: {nome}")


def main():
    print("Escolha o modo:")
    print("1 - Interface Gráfica")
    print("2 - Terminal")

    escolha = input("\nOpção [1]: ").strip()

    if escolha == '2':
        modo_terminal()
    else:
        app = InterfaceGrafica()
        app.executar()


if __name__ == "__main__":
    main()
