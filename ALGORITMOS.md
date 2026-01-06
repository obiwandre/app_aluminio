# Algoritmos de Otimização de Corte

Este documento explica os 3 algoritmos implementados no Otimizador de Corte de Barras de Alumínio.

## O Problema

O **Problema de Corte de Estoque** (Cutting Stock Problem) é um problema clássico de otimização:
- Você tem barras de tamanho fixo (ex: 600cm)
- Precisa cortar peças de tamanhos variados
- Objetivo: usar o menor número de barras possível e/ou minimizar desperdício

Este problema é **NP-difícil**, ou seja, não existe algoritmo que encontre a solução perfeita em tempo razoável para muitas peças. Por isso usamos **heurísticas** (algoritmos que encontram boas soluções rapidamente).

---

## 1. First Fit Decreasing (FFD)

### Como funciona:
1. **Ordena** todas as peças do maior para o menor
2. Para cada peça (começando pela maior):
   - Tenta colocar na **primeira barra** que tiver espaço
   - Se não couber em nenhuma, abre uma **nova barra**

### Exemplo:
```
Peças: 75, 75, 40, 40, 56, 56 (já ordenadas: 75, 75, 56, 56, 40, 40)
Barra: 600cm

Passo 1: 75cm → Barra 1 [75] (sobra 525)
Passo 2: 75cm → Barra 1 [75, 75] (sobra 450)
Passo 3: 56cm → Barra 1 [75, 75, 56] (sobra 394)
Passo 4: 56cm → Barra 1 [75, 75, 56, 56] (sobra 338)
Passo 5: 40cm → Barra 1 [75, 75, 56, 56, 40] (sobra 298)
Passo 6: 40cm → Barra 1 [75, 75, 56, 56, 40, 40] (sobra 258)

Resultado: 1 barra, sobra de 258cm
```

### Vantagens:
- Muito rápido (O(n log n))
- Simples de implementar
- Geralmente usa poucas barras

### Desvantagens:
- Não garante a solução ótima
- Pode deixar sobras pequenas espalhadas

---

## 2. Best Fit Decreasing (BFD)

### Como funciona:
1. **Ordena** todas as peças do maior para o menor
2. Para cada peça (começando pela maior):
   - Procura a barra onde a peça **deixa a menor sobra** possível
   - Se não couber em nenhuma, abre uma **nova barra**

### Diferença do FFD:
- FFD: coloca na **primeira** barra que couber
- BFD: coloca na barra que **melhor se encaixa** (menor desperdício)

### Exemplo:
```
Peças: 75, 56, 40
Barras existentes: Barra 1 (sobra 100cm), Barra 2 (sobra 80cm)

FFD colocaria 75cm na Barra 1 (primeira que cabe)
BFD colocaria 75cm na Barra 1 também (100-75=25 < 80-75=5... ops, não cabe na 2!)

Mas se fosse 40cm:
- Barra 1: 100 - 40 = 60cm de sobra
- Barra 2: 80 - 40 = 40cm de sobra
FFD → Barra 1
BFD → Barra 2 (menor sobra = melhor encaixe)
```

### Vantagens:
- Tende a preencher melhor as barras
- Reduz fragmentação (sobras pequenas)

### Desvantagens:
- Um pouco mais lento que FFD
- Ainda não garante solução ótima

---

## 3. Otimizado para Maiores Sobras

### Como funciona:
1. Para cada iteração:
   - Testa **todas as combinações** de peças restantes
   - Escolhe a combinação que **usa mais material** em uma barra
2. Remove as peças usadas e repete

### Objetivo:
Concentrar o uso de material em poucas barras, deixando **sobras grandes e úteis** em vez de várias sobras pequenas.

### Exemplo:
```
Peças: 75, 75, 75, 75, 56, 56, 40, 40
Barra: 600cm

Iteração 1: Qual combo usa mais da barra?
- 75+75+75+75+56+56+40 = 452cm ✗ (passa de 600 com cortes)
- 75+75+75+75+75+75+75+75 = 600cm ✓ (8x75 = 600 exato!)

Barra 1: [75, 75, 75, 75, 75, 75, 75, 75] → sobra 0cm

Iteração 2: Peças restantes: 56, 56, 40, 40
- 56+56+40+40 = 192cm

Barra 2: [56, 56, 40, 40] → sobra 408cm (uma sobra GRANDE e útil!)
```

### Vantagens:
- Maximiza sobras úteis (reaproveitáveis)
- Evita "cotocos" pequenos inúteis
- Melhor para quem quer reaproveitar material

### Desvantagens:
- Mais lento (testa mais combinações)
- Pode usar mais barras em alguns casos

---

## Comparação Resumida

| Algoritmo | Velocidade | Nº de Barras | Sobras |
|-----------|------------|--------------|--------|
| **FFD** | Muito rápido | Bom | Variadas |
| **BFD** | Rápido | Muito bom | Menores |
| **Maiores Sobras** | Médio | Bom | Grandes e úteis |

---

## Qual o Programa Escolhe?

O programa **testa os 3 algoritmos** e escolhe automaticamente o melhor resultado baseado em:

1. **Menor número de barras** (prioridade máxima)
2. **Maior sobra útil** (desempate)

Assim você sempre tem o resultado mais econômico!

---

## Referências

- [Bin Packing Problem - Wikipedia](https://en.wikipedia.org/wiki/Bin_packing_problem)
- [Cutting Stock Problem - Wikipedia](https://en.wikipedia.org/wiki/Cutting_stock_problem)
- Martello, S., & Toth, P. (1990). *Knapsack Problems: Algorithms and Computer Implementations*
