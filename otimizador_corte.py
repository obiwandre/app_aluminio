"""
Otimizador de Corte de Barras de Alumínio
Objetivo: Minimizar desperdício e maximizar sobras úteis
"""

from itertools import permutations
from typing import List, Tuple

# Configuração
TAMANHO_BARRA = 600  # cm

# Peças necessárias (em cm)
pecas_necessarias = [
    # Quadro 1: 75x75x40x40
    75, 75, 40, 40,
    # Quadro 2: 56x56x75x75
    56, 56, 75, 75,
    # Quadro 3: 36x36x75x75
    36, 36, 75, 75,
    # Quadro 4: 34x34x75x75
    34, 34, 75, 75,
]

def calcular_cortes_greedy(pecas: List[int], tamanho_barra: int) -> List[List[int]]:
    """
    Algoritmo guloso: coloca as maiores peças primeiro em cada barra.
    Estratégia: First Fit Decreasing (FFD)
    """
    pecas_ordenadas = sorted(pecas, reverse=True)  # Maiores primeiro
    barras = []  # Lista de barras, cada uma com suas peças

    for peca in pecas_ordenadas:
        colocada = False
        # Tenta colocar na barra existente com mais espaço que caiba
        for i, barra in enumerate(barras):
            espaco_usado = sum(barra)
            if espaco_usado + peca <= tamanho_barra:
                barras[i].append(peca)
                colocada = True
                break

        # Se não coube em nenhuma, abre nova barra
        if not colocada:
            barras.append([peca])

    return barras


def calcular_cortes_best_fit(pecas: List[int], tamanho_barra: int) -> List[List[int]]:
    """
    Best Fit Decreasing: coloca cada peça na barra onde sobra menos espaço
    (minimiza desperdício por barra)
    """
    pecas_ordenadas = sorted(pecas, reverse=True)
    barras = []

    for peca in pecas_ordenadas:
        melhor_barra = -1
        menor_sobra = tamanho_barra + 1

        for i, barra in enumerate(barras):
            espaco_usado = sum(barra)
            sobra = tamanho_barra - espaco_usado - peca
            if sobra >= 0 and sobra < menor_sobra:
                melhor_barra = i
                menor_sobra = sobra

        if melhor_barra >= 0:
            barras[melhor_barra].append(peca)
        else:
            barras.append([peca])

    return barras


def analisar_resultado(barras: List[List[int]], tamanho_barra: int, nome: str):
    """Analisa e imprime os resultados de um plano de corte"""
    print(f"\n{'='*60}")
    print(f"PLANO DE CORTE: {nome}")
    print(f"{'='*60}")

    total_sobras = 0
    sobras_list = []

    for i, barra in enumerate(barras, 1):
        usado = sum(barra)
        sobra = tamanho_barra - usado
        total_sobras += sobra
        sobras_list.append(sobra)

        # Ordena peças para exibição
        pecas_str = " + ".join(f"{p}cm" for p in sorted(barra, reverse=True))
        print(f"\nBarra {i}: {pecas_str}")
        print(f"         Total usado: {usado}cm | Sobra: {sobra}cm")

    print(f"\n{'-'*60}")
    print(f"RESUMO:")
    print(f"  - Barras necessárias: {len(barras)} barras de {tamanho_barra}cm")
    print(f"  - Material total: {len(barras) * tamanho_barra}cm")
    print(f"  - Material usado: {sum(sum(b) for b in barras)}cm")
    print(f"  - Sobra total: {total_sobras}cm")
    print(f"  - Eficiência: {(1 - total_sobras/(len(barras)*tamanho_barra))*100:.1f}%")
    print(f"\n  Sobras por barra: {sorted(sobras_list, reverse=True)}")

    return sobras_list


def otimizar_para_maiores_sobras(pecas: List[int], tamanho_barra: int) -> List[List[int]]:
    """
    Tenta agrupar peças de forma que as sobras sejam as maiores possíveis
    (concentra o desperdício em poucas barras, deixando sobras grandes nas outras)
    """
    pecas_ordenadas = sorted(pecas, reverse=True)
    barras = []

    # Primeiro, tenta preencher barras o mais completo possível
    # deixando uma barra com sobra grande

    pecas_restantes = pecas_ordenadas.copy()

    while pecas_restantes:
        # Tenta encontrar combinação que chegue mais perto de 600
        melhor_combo = None
        melhor_uso = 0

        # Para cada peça restante como início
        for i, peca in enumerate(pecas_restantes):
            combo = [peca]
            uso = peca
            restantes_temp = pecas_restantes[:i] + pecas_restantes[i+1:]

            # Adiciona mais peças enquanto couber
            for p in restantes_temp:
                if uso + p <= tamanho_barra:
                    combo.append(p)
                    uso += p

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


def main():
    print("="*60)
    print("OTIMIZADOR DE CORTE DE BARRAS DE ALUMÍNIO")
    print("="*60)

    print(f"\nTamanho da barra: {TAMANHO_BARRA}cm")
    print(f"\nPeças necessárias ({len(pecas_necessarias)} peças):")

    # Agrupa por tamanho para exibição
    from collections import Counter
    contagem = Counter(pecas_necessarias)
    for tamanho, qtd in sorted(contagem.items(), reverse=True):
        print(f"  - {qtd}x {tamanho}cm")

    print(f"\nTotal de material necessário: {sum(pecas_necessarias)}cm")
    print(f"Mínimo teórico de barras: {sum(pecas_necessarias)/TAMANHO_BARRA:.2f} = {-(-sum(pecas_necessarias)//TAMANHO_BARRA)} barras")

    # Testa diferentes algoritmos
    resultado_ffd = calcular_cortes_greedy(pecas_necessarias, TAMANHO_BARRA)
    sobras_ffd = analisar_resultado(resultado_ffd, TAMANHO_BARRA, "First Fit Decreasing (Guloso)")

    resultado_bfd = calcular_cortes_best_fit(pecas_necessarias, TAMANHO_BARRA)
    sobras_bfd = analisar_resultado(resultado_bfd, TAMANHO_BARRA, "Best Fit Decreasing")

    resultado_otim = otimizar_para_maiores_sobras(pecas_necessarias, TAMANHO_BARRA)
    sobras_otim = analisar_resultado(resultado_otim, TAMANHO_BARRA, "Otimizado para Maiores Sobras")

    # Recomendação
    print("\n" + "="*60)
    print("RECOMENDAÇÃO FINAL")
    print("="*60)

    # Escolhe o que tem sobras maiores (mais úteis)
    maior_sobra_ffd = max(sobras_ffd)
    maior_sobra_bfd = max(sobras_bfd)
    maior_sobra_otim = max(sobras_otim)

    print(f"\nMaior sobra útil por método:")
    print(f"  - FFD: {maior_sobra_ffd}cm")
    print(f"  - BFD: {maior_sobra_bfd}cm")
    print(f"  - Otimizado: {maior_sobra_otim}cm")

    # Usa BFD como padrão pois geralmente dá bons resultados
    print(f"\n>>> Você precisará de {len(resultado_bfd)} BARRAS de 600cm <<<")


if __name__ == "__main__":
    main()
