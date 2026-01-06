"""
Otimizador de Corte de Barras de Alumínio
Versão: 0.0.2
Objetivo: Minimizar desperdício e maximizar sobras úteis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Tuple
from collections import Counter
from datetime import datetime
import csv


class OtimizadorCorte:
    """Classe principal com algoritmos de otimização"""

    def __init__(self, tamanho_barra: float = 600, espessura_corte: float = 0):
        self.tamanho_barra = tamanho_barra
        self.espessura_corte = espessura_corte

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
                # Considera espessura do corte para cada peça já na barra
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

    def analisar_resultado(self, barras: List[List[float]]) -> dict:
        """Retorna análise completa do resultado"""
        sobras = [self.calcular_sobra(b) for b in barras]
        material_usado = sum(sum(b) for b in barras)
        material_total = len(barras) * self.tamanho_barra

        return {
            'barras': barras,
            'num_barras': len(barras),
            'sobras': sobras,
            'sobra_total': sum(sobras),
            'material_usado': material_usado,
            'material_total': material_total,
            'eficiencia': (material_usado / material_total * 100) if material_total > 0 else 0
        }


class InterfaceGrafica:
    """Interface gráfica com Tkinter"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Otimizador de Corte de Barras de Alumínio v0.0.2")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        self.pecas = []
        self.ultimo_resultado = None

        self.criar_interface()

    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)

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

        # === Entrada de peças ===
        input_frame = ttk.LabelFrame(main_frame, text="Adicionar Peças", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

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
        quadro_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(quadro_frame, text="Medidas do quadro (ex: 75x75x40x40):").grid(row=0, column=0, padx=5)
        self.entry_quadro = ttk.Entry(quadro_frame, width=20)
        self.entry_quadro.grid(row=0, column=1, padx=5)
        self.entry_quadro.bind('<Return>', lambda e: self.adicionar_quadro())

        ttk.Button(quadro_frame, text="Adicionar Quadro", command=self.adicionar_quadro).grid(row=0, column=2, padx=5)

        # === Lista de peças ===
        lista_frame = ttk.LabelFrame(main_frame, text="Peças Adicionadas", padding="10")
        lista_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10), padx=(0, 5))
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        self.lista_pecas = tk.Listbox(lista_frame, width=30, height=10)
        self.lista_pecas.grid(row=0, column=0, sticky="nsew")

        scrollbar_lista = ttk.Scrollbar(lista_frame, orient="vertical", command=self.lista_pecas.yview)
        scrollbar_lista.grid(row=0, column=1, sticky="ns")
        self.lista_pecas.config(yscrollcommand=scrollbar_lista.set)

        ttk.Button(lista_frame, text="Remover Selecionada", command=self.remover_peca).grid(row=1, column=0, pady=5)

        # === Botão calcular ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=1, sticky="n", pady=(0, 10))

        ttk.Button(btn_frame, text="CALCULAR OTIMIZAÇÃO", command=self.calcular,
                   style="Accent.TButton").grid(row=0, column=0, pady=10, ipady=10, ipadx=20)

        ttk.Button(btn_frame, text="Salvar Resultado (TXT)", command=self.salvar_txt).grid(row=1, column=0, pady=5)
        ttk.Button(btn_frame, text="Salvar Resultado (CSV)", command=self.salvar_csv).grid(row=2, column=0, pady=5)

        # === Resultado ===
        resultado_frame = ttk.LabelFrame(main_frame, text="Resultado da Otimização", padding="10")
        resultado_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")
        resultado_frame.columnconfigure(0, weight=1)
        resultado_frame.rowconfigure(0, weight=1)

        self.texto_resultado = tk.Text(resultado_frame, wrap=tk.WORD, width=80, height=15)
        self.texto_resultado.grid(row=0, column=0, sticky="nsew")

        scrollbar_resultado = ttk.Scrollbar(resultado_frame, orient="vertical", command=self.texto_resultado.yview)
        scrollbar_resultado.grid(row=0, column=1, sticky="ns")
        self.texto_resultado.config(yscrollcommand=scrollbar_resultado.set)

        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=2)

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
            # Pega o texto selecionado e extrai a medida
            texto = self.lista_pecas.get(selecao[0])
            medida = float(texto.split('x')[0].strip())
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
        self.lista_pecas.insert(tk.END, f"─" * 20)
        self.lista_pecas.insert(tk.END, f"Total: {total}cm ({len(self.pecas)} peças)")

    def calcular(self):
        if not self.pecas:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma peça!")
            return

        try:
            tamanho_barra = float(self.entry_tamanho.get().replace(',', '.'))
            espessura_mm = float(self.entry_espessura.get().replace(',', '.'))
            espessura_cm = espessura_mm / 10  # Converte mm para cm

        except ValueError:
            messagebox.showerror("Erro", "Configurações inválidas!")
            return

        # Verifica se alguma peça é maior que a barra
        for peca in self.pecas:
            if peca > tamanho_barra:
                messagebox.showerror("Erro", f"Peça de {peca}cm é maior que a barra de {tamanho_barra}cm!")
                return

        otimizador = OtimizadorCorte(tamanho_barra, espessura_cm)

        # Calcula com os 3 métodos
        resultado_ffd = otimizador.analisar_resultado(otimizador.calcular_cortes_greedy(self.pecas))
        resultado_bfd = otimizador.analisar_resultado(otimizador.calcular_cortes_best_fit(self.pecas))
        resultado_otim = otimizador.analisar_resultado(otimizador.otimizar_para_maiores_sobras(self.pecas))

        # Escolhe o melhor (menor número de barras, depois maior sobra útil)
        resultados = [
            ('First Fit Decreasing', resultado_ffd),
            ('Best Fit Decreasing', resultado_bfd),
            ('Otimizado p/ Maiores Sobras', resultado_otim)
        ]

        # Ordena: menos barras primeiro, depois maior sobra máxima
        melhor_nome, melhor = min(resultados, key=lambda x: (x[1]['num_barras'], -max(x[1]['sobras'])))

        self.ultimo_resultado = {
            'tamanho_barra': tamanho_barra,
            'espessura_corte': espessura_mm,
            'pecas': self.pecas.copy(),
            'metodo': melhor_nome,
            'resultado': melhor
        }

        # Exibe resultado
        self.texto_resultado.delete(1.0, tk.END)

        texto = "=" * 60 + "\n"
        texto += "RESULTADO DA OTIMIZAÇÃO\n"
        texto += "=" * 60 + "\n\n"

        texto += f"Configurações:\n"
        texto += f"  - Tamanho da barra: {tamanho_barra}cm\n"
        texto += f"  - Espessura do corte: {espessura_mm}mm\n"
        texto += f"  - Total de peças: {len(self.pecas)}\n"
        texto += f"  - Método usado: {melhor_nome}\n\n"

        texto += "-" * 60 + "\n"
        texto += f">>> VOCÊ PRECISARÁ DE {melhor['num_barras']} BARRA(S) <<<\n"
        texto += "-" * 60 + "\n\n"

        texto += "PLANO DE CORTE:\n\n"

        for i, barra in enumerate(melhor['barras'], 1):
            sobra = otimizador.calcular_sobra(barra)
            pecas_str = " + ".join(f"{p}cm" for p in sorted(barra, reverse=True))
            texto += f"Barra {i}:\n"
            texto += f"  Cortes: {pecas_str}\n"
            texto += f"  Usado: {sum(barra):.1f}cm | Sobra: {sobra:.1f}cm\n\n"

        texto += "-" * 60 + "\n"
        texto += "RESUMO:\n"
        texto += f"  - Material total: {melhor['material_total']:.1f}cm\n"
        texto += f"  - Material usado: {melhor['material_usado']:.1f}cm\n"
        texto += f"  - Sobra total: {melhor['sobra_total']:.1f}cm\n"
        texto += f"  - Eficiência: {melhor['eficiencia']:.1f}%\n"
        texto += f"  - Sobras por barra: {[f'{s:.1f}cm' for s in sorted(melhor['sobras'], reverse=True)]}\n"

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

                # Cabeçalho
                writer.writerow(['OTIMIZADOR DE CORTE DE BARRAS DE ALUMÍNIO'])
                writer.writerow(['Data', datetime.now().strftime('%d/%m/%Y %H:%M')])
                writer.writerow(['Tamanho da Barra (cm)', resultado['tamanho_barra']])
                writer.writerow(['Espessura do Corte (mm)', resultado['espessura_corte']])
                writer.writerow(['Método', resultado['metodo']])
                writer.writerow([])

                # Peças necessárias
                writer.writerow(['PEÇAS NECESSÁRIAS'])
                writer.writerow(['Medida (cm)', 'Quantidade'])
                contagem = Counter(resultado['pecas'])
                for medida, qtd in sorted(contagem.items(), reverse=True):
                    writer.writerow([medida, qtd])
                writer.writerow([])

                # Plano de corte
                writer.writerow(['PLANO DE CORTE'])
                writer.writerow(['Barra', 'Peças (cm)', 'Total Usado (cm)', 'Sobra (cm)'])

                otimizador = OtimizadorCorte(resultado['tamanho_barra'], resultado['espessura_corte']/10)
                for i, barra in enumerate(resultado['resultado']['barras'], 1):
                    pecas_str = ' + '.join(str(p) for p in sorted(barra, reverse=True))
                    sobra = otimizador.calcular_sobra(barra)
                    writer.writerow([i, pecas_str, sum(barra), f'{sobra:.1f}'])

                writer.writerow([])
                writer.writerow(['RESUMO'])
                writer.writerow(['Total de Barras', resultado['resultado']['num_barras']])
                writer.writerow(['Eficiência', f"{resultado['resultado']['eficiencia']:.1f}%"])

            messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{filepath}")

    def executar(self):
        self.root.mainloop()


def modo_terminal():
    """Modo interativo via terminal"""
    print("=" * 60)
    print("OTIMIZADOR DE CORTE DE BARRAS DE ALUMÍNIO v0.0.2")
    print("=" * 60)

    # Configurações
    tamanho_input = input("\nTamanho da barra em cm [600]: ").strip()
    tamanho_barra = float(tamanho_input) if tamanho_input else 600

    espessura_input = input("Espessura do corte em mm [3]: ").strip()
    espessura_mm = float(espessura_input) if espessura_input else 3
    espessura_cm = espessura_mm / 10

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
                # Apenas medida
                pecas.append(float(partes[0]))
            elif len(partes) == 2:
                # medidaxquantidade
                medida = float(partes[0])
                qtd = int(partes[1])
                pecas.extend([medida] * qtd)
            elif len(partes) == 4:
                # Quadro: 4 medidas
                for p in partes:
                    pecas.append(float(p))
            else:
                print("Formato inválido!")
                continue

            print(f"  Adicionado! Total: {len(pecas)} peças ({sum(pecas)}cm)")

        except ValueError:
            print("Valor inválido!")

    # Calcula
    otimizador = OtimizadorCorte(tamanho_barra, espessura_cm)

    resultado_ffd = otimizador.analisar_resultado(otimizador.calcular_cortes_greedy(pecas))
    resultado_bfd = otimizador.analisar_resultado(otimizador.calcular_cortes_best_fit(pecas))
    resultado_otim = otimizador.analisar_resultado(otimizador.otimizar_para_maiores_sobras(pecas))

    resultados = [
        ('First Fit Decreasing', resultado_ffd),
        ('Best Fit Decreasing', resultado_bfd),
        ('Otimizado p/ Maiores Sobras', resultado_otim)
    ]

    melhor_nome, melhor = min(resultados, key=lambda x: (x[1]['num_barras'], -max(x[1]['sobras'])))

    # Exibe resultado
    print("\n" + "=" * 60)
    print("RESULTADO DA OTIMIZAÇÃO")
    print("=" * 60)

    print(f"\nConfiguração: Barra {tamanho_barra}cm, Corte {espessura_mm}mm")
    print(f"Método: {melhor_nome}")

    print("\n" + "-" * 60)
    print(f">>> VOCÊ PRECISARÁ DE {melhor['num_barras']} BARRA(S) <<<")
    print("-" * 60)

    print("\nPLANO DE CORTE:\n")

    for i, barra in enumerate(melhor['barras'], 1):
        sobra = otimizador.calcular_sobra(barra)
        pecas_str = " + ".join(f"{p}cm" for p in sorted(barra, reverse=True))
        print(f"Barra {i}: {pecas_str}")
        print(f"         Usado: {sum(barra):.1f}cm | Sobra: {sobra:.1f}cm\n")

    print("-" * 60)
    print(f"Eficiência: {melhor['eficiencia']:.1f}%")
    print(f"Sobras: {[f'{s:.1f}cm' for s in sorted(melhor['sobras'], reverse=True)]}")

    # Pergunta se quer salvar
    salvar = input("\nSalvar resultado? (txt/csv/n): ").strip().lower()

    if salvar == 'txt':
        nome = f"corte_aluminio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(nome, 'w', encoding='utf-8') as f:
            f.write(f"OTIMIZADOR DE CORTE - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Barra: {tamanho_barra}cm | Corte: {espessura_mm}mm\n")
            f.write(f"Barras necessárias: {melhor['num_barras']}\n\n")
            for i, barra in enumerate(melhor['barras'], 1):
                sobra = otimizador.calcular_sobra(barra)
                f.write(f"Barra {i}: {' + '.join(f'{p}cm' for p in sorted(barra, reverse=True))}\n")
                f.write(f"         Sobra: {sobra:.1f}cm\n\n")
        print(f"Salvo em: {nome}")

    elif salvar == 'csv':
        nome = f"corte_aluminio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(nome, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Barra', 'Peças', 'Sobra (cm)'])
            for i, barra in enumerate(melhor['barras'], 1):
                sobra = otimizador.calcular_sobra(barra)
                writer.writerow([i, ' + '.join(str(p) for p in barra), f'{sobra:.1f}'])
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
