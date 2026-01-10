# Documentação do Pipeline de Extração do Catálogo Aluminovo 2025

## Visão Geral

Este documento descreve o processo completo de extração de dados do catálogo PDF para um formato estruturado JSON.

---

## Arquivos do Sistema

```
leitor_catalogo/catalogos/
├── catalogo-aluminovo_2025.pdf       # PDF original do catálogo
├── extrair_todas_paginas.py          # Script que converte PDF → PNGs
├── marcador_catalogo.py              # Interface Tkinter para marcação
├── extrair_dados.py                  # Pipeline de extração de dados
├── visualizador_dados.py             # Interface Tkinter para visualizar dados extraídos
├── marcacoes.json                    # Coordenadas das marcações (gerado)
├── dados_catalogo.json               # Dados extraídos finais (gerado)
├── extracao_conferencia/             # Pasta com imagens
│   ├── pagina_XX_original.png        # Imagens originais do PDF
│   └── pagina_XX_marcada.png         # Imagens com marcações visuais
└── recortes/                         # Imagens recortadas das áreas marcadas
    └── pagXX_Categoria/              # Pasta por página/categoria
        ├── Item_NOME.png             # Recorte do título
        ├── Item_IMAGEM.png           # Recorte do desenho técnico
        └── Item_TABELA.png           # Recorte da tabela
```

---

## Pipeline em 4 Etapas

### ETAPA 1: Extrair Páginas do PDF

**Objetivo:** Converter cada página do PDF em uma imagem PNG.

**Comando:**
```bash
python extrair_todas_paginas.py
```

**O que faz:**
- Abre o PDF com PyMuPDF (fitz)
- Renderiza cada página em 150 DPI
- Salva como `pagina_XX_original.png` na pasta `extracao_conferencia/`

**Resultado:** 132 arquivos PNG (um por página)

---

### ETAPA 2: Marcar Áreas no Tkinter (MODO SEMI-AUTOMÁTICO COM OCR)

**Objetivo:** Usuário marca visualmente as áreas de interesse em cada página.

**Comando:**
```bash
python marcador_catalogo.py
```

**Interface:**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Navegação] [Categoria] [Modo] [▶ INICIAR ITEM] [Item Atual] [Marcando] [Ações]│
├──────────────────────────────────────────────────────────────────────────────┤
│ Lista de   │                                                                 │
│ Itens      │              IMAGEM DA PÁGINA                                   │
│            │                                                                 │
│ - Item 1   │     (usuário desenha retângulos aqui)                           │
│ - Item 2   │                                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ Status: ✏ Desenhe o retângulo do NOME do item                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## MODO SEMI-AUTOMÁTICO COM OCR (RECOMENDADO)

O marcador possui um **modo semi-automático** que acelera muito o processo de marcação!

### Como Funciona:

1. **Clique em [▶ INICIAR ITEM]**
   - Se for a primeira vez na página, pergunta a categoria
   - Sugere a última categoria usada (ex: "Perfis Tabelados")

2. **Desenhe o retângulo no NOME do item**
   - O indicador mostra "NOME" em vermelho
   - Desenhe o retângulo em volta do título do item

3. **OCR Automático detecta o nome!**
   - O sistema faz OCR na região desenhada
   - Abre diálogo: `OCR detectou: "Tubo Redondo" - Confirme ou corrija`
   - Basta clicar OK se estiver correto, ou corrigir se necessário

4. **Automaticamente muda para IMAGEM**
   - O indicador muda para "IMAGEM" em azul
   - Desenhe o retângulo no desenho técnico (incluindo letras A, B, E)

5. **Automaticamente muda para TABELA**
   - O indicador muda para "TABELA" em verde
   - Desenhe o retângulo na tabela de dados

6. **Pergunta se quer salvar e iniciar próximo**
   - Clica "Sim" → Salva e já inicia próximo item
   - Clica "Não" → Salva e para

### Benefícios do Modo Semi-Automático:
- **OCR automático** - não precisa digitar nome do item
- **Fluxo guiado** - indica qual marcação fazer
- **Cores no indicador** - mostra visualmente o que está marcando
- **Salva automático** - pergunta se quer salvar ao finalizar
- **Loop contínuo** - pode marcar vários itens em sequência

### Botões Úteis:
- **Desfazer** - remove última marcação e volta para ela
- **Cancelar Item** - descarta item atual e suas marcações
- **Mudar** (categoria) - altera categoria da página

---

## Fluxo Manual (alternativo)

Se desmarcar "Semi-Automático", o fluxo tradicional é:

1. **Navegar** para a página desejada (ex: página 6)

2. **Definir Categoria** (botão "Mudar")
   - Ex: "Perfis Tabelados", "Contra Marcos", etc.
   - A categoria agrupa todos os itens da página

3. **Criar Item** (botão "+ Novo")
   - Digitar nome do item: "Tubo Redondo"
   - O item fica selecionado automaticamente

4. **Marcar as 3 áreas** do item:
   - Selecionar tipo **NOME** → desenhar retângulo no título
   - Selecionar tipo **IMAGEM** → desenhar retângulo no desenho técnico
   - Selecionar tipo **TABELA** → desenhar retângulo na tabela de dados

5. **Repetir** para cada item da página (ex: "Tubo Quadrado")

6. **Salvar** (botão "Salvar")
   - Grava `marcacoes.json`

**Estrutura do marcacoes.json:**
```json
{
  "6": {
    "categoria": "Perfis Tabelados",
    "itens": [
      {
        "nome": "Tubo Redondo",
        "marcacoes": {
          "nome": [x1, y1, x2, y2],
          "imagem": [x1, y1, x2, y2],
          "tabela": [x1, y1, x2, y2]
        }
      }
    ]
  }
}
```

**Cores das Marcações:**
- **NOME** = Vermelho (#FF0000)
- **IMAGEM** = Azul (#0066FF)
- **TABELA** = Verde (#00CC00)

---

### ETAPA 3: Recortar Áreas Marcadas

**Objetivo:** Gerar imagens recortadas de cada área para análise.

**Comando:**
```bash
python extrair_dados.py
```

**O que faz:**
- Lê `marcacoes.json`
- Para cada item marcado:
  - Recorta a área NOME → salva `Item_NOME.png`
  - Recorta a área IMAGEM → salva `Item_IMAGEM.png`
  - Recorta a área TABELA → salva `Item_TABELA.png`
- Salva na pasta `recortes/pagXX_Categoria/`

**Resultado:** Imagens individuais de cada elemento para análise

---

### ETAPA 4: Extrair Dados (Claude lê as imagens)

**Objetivo:** Converter as imagens das tabelas em dados estruturados.

**Processo:**
1. Claude (IA) abre cada imagem de TABELA recortada
2. Lê visualmente os dados da tabela
3. Transcreve para o formato JSON
4. Salva em `dados_catalogo.json`

**Por que não OCR automático?**
- Tesseract tem dificuldade com tabelas complexas
- Dados críticos (códigos, medidas) precisam de 100% de precisão
- Claude consegue ler imagens com precisão total

**Comando para salvar dados extraídos:**
```bash
python extrair_dados.py --extrair
```

**Estrutura do dados_catalogo.json:**
```json
[
  {
    "pagina": 6,
    "categoria": "Perfis Tabelados",
    "itens": [
      {
        "nome": "Tubo Redondo",
        "tabela": {
          "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada E", "Milímetro A", "Milímetro E"],
          "linhas": [
            ["TR3/8*100", "0,072", "3/8\"", "-", "9,52", "1,00"],
            ["TR3/8*158", "0,108", "3/8\"", "1/16\"", "9,52", "1,58"]
          ]
        }
      }
    ]
  }
]
```

---

## Fluxo de Trabalho Resumido

```
┌─────────────────┐
│   PDF Original  │
└────────┬────────┘
         │ extrair_todas_paginas.py
         ▼
┌─────────────────┐
│  PNGs Originais │  (pagina_XX_original.png)
└────────┬────────┘
         │ marcador_catalogo.py (usuário marca)
         ▼
┌─────────────────┐
│ marcacoes.json  │  (coordenadas das áreas)
└────────┬────────┘
         │ extrair_dados.py (recorta áreas)
         ▼
┌─────────────────┐
│ Imagens Recort. │  (recortes/Item_TABELA.png)
└────────┬────────┘
         │ Claude lê e transcreve
         ▼
┌─────────────────┐
│dados_catalogo.json│  (dados estruturados)
└─────────────────┘
```

---

## Comandos Rápidos

```bash
# 1. Extrair páginas do PDF (só precisa fazer 1 vez)
python extrair_todas_paginas.py

# 2. Abrir marcador para marcar páginas
python marcador_catalogo.py

# 3. Recortar áreas marcadas
python extrair_dados.py

# 4. Salvar dados extraídos pelo Claude
python extrair_dados.py --extrair
```

---

## Como Adicionar Dados de Nova Página

### Passo 1: Marcar a página no Tkinter
```bash
python marcador_catalogo.py
```
1. Navegar até a página desejada
2. Clicar "Definir" e digitar a categoria (ex: "Perfis Tabelados")
3. Clicar "+ Novo" e digitar o nome do item (ex: "Tubo Redondo")
4. Selecionar "NOME" e desenhar retângulo no título
5. Selecionar "IMAGEM" e desenhar retângulo no desenho técnico
6. Selecionar "TABELA" e desenhar retângulo na tabela
7. Repetir para cada item da página
8. Clicar "Salvar"

### Passo 2: Gerar recortes das áreas marcadas
```bash
python extrair_dados.py
```
Isso recorta as áreas marcadas e salva em `recortes/pagXX_Categoria/`

### Passo 3: Pedir para Claude extrair os dados
Enviar mensagem para Claude:
```
Marcou mais páginas. Extraia os dados.
```

Claude vai:
1. Ler as imagens das tabelas em `recortes/`
2. Transcrever os dados manualmente (100% precisão)
3. Adicionar no arquivo `extrair_dados.py` como `DADOS_PAGINA_X`

### Passo 4: Salvar os dados no JSON
```bash
python extrair_dados.py --extrair
```

### Passo 5: Visualizar os dados extraídos
```bash
python visualizador_dados.py
```
Interface mostra:
- Árvore de navegação (Página → Itens)
- Imagem do perfil
- Tabela com todos os dados

---

## IMPORTANTE: Como Claude Extrai os Dados

### Por que não usar OCR automático?
O Tesseract (OCR) tem dificuldade com tabelas e gera muitos erros.
Como os dados são críticos (códigos, medidas, pesos), usamos Claude para ler as imagens diretamente.

### Processo de Extração pelo Claude

1. **Claude lê a imagem da tabela**
   ```
   Read c:\Projects\app_aluminio\leitor_catalogo\catalogos\recortes\pag07_Perfis_Tabelados\Tubo_Retangular_TABELA.png
   ```

2. **Claude transcreve os dados** olhando a imagem e cria um dicionário Python:
   ```python
   DADOS_PAGINA_7 = {
       "pagina": 7,
       "categoria": "Perfis Tabelados",
       "itens": [
           {
               "nome": "Tubo Retangular",
               "tabela": {
                   "cabecalho": ["Código", "Kg/metro", ...],
                   "linhas": [
                       ["1704L", "0,230", ...],
                       ...
                   ]
               }
           }
       ]
   }
   ```

3. **Claude adiciona ao arquivo `extrair_dados.py`**
   - Cria a variável `DADOS_PAGINA_X`
   - Adiciona na lista em `salvar_dados_extraidos()`

4. **Executa para salvar no JSON**
   ```bash
   python extrair_dados.py --extrair
   ```

### Exemplo de Comando para Claude

Após marcar novas páginas, dizer:
```
Marquei as páginas 8 e 9.
Execute python extrair_dados.py para gerar os recortes.
Depois leia as imagens das tabelas e extraia os dados.
```

---

## MÉTODO DETALHADO: Como Claude Extrai Tabelas (PASSO A PASSO)

### PASSO 1: Gerar os recortes
```bash
python extrair_dados.py
```
Isso cria a pasta `recortes/pagXX_Categoria/` com as imagens recortadas.

### PASSO 2: Claude lê CADA imagem de tabela
Para cada item marcado, Claude deve ler a imagem da tabela:
```
Read c:\Projects\app_aluminio\leitor_catalogo\catalogos\recortes\pag07_Perfis_Tabelados\Tubo_Retangular_TABELA.png
```

### PASSO 3: Claude analisa a tabela visualmente
Olhando a imagem, identificar:
1. **Cabeçalho** - primeira linha com nomes das colunas
2. **Linhas de dados** - todas as linhas abaixo do cabeçalho
3. **Número de colunas** - contar quantas colunas tem

### PASSO 4: Claude transcreve os dados EXATAMENTE como aparecem
**IMPORTANTE:**
- Copiar os valores EXATAMENTE como aparecem na imagem
- Usar vírgula para decimais (padrão brasileiro): `0,072` não `0.072`
- Manter aspas nas polegadas: `3/8"` não `3/8`
- Usar hífen para valores vazios: `-`
- Verificar CADA linha, não pular nenhuma

### PASSO 5: Criar o dicionário Python
```python
DADOS_PAGINA_X = {
    "pagina": X,
    "categoria": "Nome da Categoria",
    "itens": [
        {
            "nome": "Nome do Item",
            "tabela": {
                "cabecalho": ["Col1", "Col2", "Col3", ...],
                "linhas": [
                    ["val1", "val2", "val3", ...],
                    ["val1", "val2", "val3", ...],
                    # ... todas as linhas
                ]
            }
        }
    ]
}
```

### PASSO 6: Adicionar ao arquivo extrair_dados.py
1. Adicionar a variável `DADOS_PAGINA_X` antes da função `salvar_dados_extraidos()`
2. Adicionar `DADOS_PAGINA_X` na lista dentro de `salvar_dados_extraidos()`:
```python
def salvar_dados_extraidos():
    dados_completos = [DADOS_PAGINA_6, DADOS_PAGINA_7, DADOS_PAGINA_X]  # <- adicionar aqui
```

### PASSO 7: Executar para salvar no JSON
```bash
python extrair_dados.py --extrair
```

### PASSO 8: Verificar no visualizador
```bash
python visualizador_dados.py
```

---

## CHECKLIST DE VERIFICAÇÃO (Claude deve seguir)

Antes de finalizar a extração, verificar:

- [ ] Li a imagem da tabela com o comando Read?
- [ ] Contei o número correto de colunas?
- [ ] O cabeçalho está completo e correto?
- [ ] Todas as linhas foram transcritas?
- [ ] Os valores decimais usam vírgula (0,072)?
- [ ] As polegadas têm aspas (3/8")?
- [ ] Valores vazios estão como "-"?
- [ ] Adicionei DADOS_PAGINA_X no extrair_dados.py?
- [ ] Adicionei na lista em salvar_dados_extraidos()?
- [ ] Executei python extrair_dados.py --extrair?

---

## EXEMPLO COMPLETO DE EXTRAÇÃO

### 1. Ler a imagem
```
Read c:\Projects\app_aluminio\leitor_catalogo\catalogos\recortes\pag06_Perfis_Tabelados\Tubo_Redondo_TABELA.png
```

### 2. Analisar (Claude vê a imagem e identifica):
- Cabeçalho: REDONDO | Código | Kg/metro | POLEGADA A | E | MILÍMETRO A | E
- 12 linhas de dados
- 6 colunas de dados úteis

### 3. Transcrever:
```python
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
                    # ... continua com TODAS as linhas
                ]
            }
        }
    ]
}
```

### 4. Adicionar no extrair_dados.py e executar:
```bash
python extrair_dados.py --extrair
```

---

## Estrutura de Dados por Tipo de Perfil

### Perfis Tabelados (Tubo Redondo, Tubo Quadrado)
```json
{
  "cabecalho": ["Código", "Kg/metro", "Polegada A", "Polegada E", "Milímetro A", "Milímetro E"],
  "linhas": [["TR3/8*100", "0,072", "3/8\"", "-", "9,52", "1,00"]]
}
```

### Outros tipos (adaptar conforme necessário)
- Contra Marcos: podem ter colunas diferentes
- Linhas especiais: verificar cabeçalho de cada tabela

---

## Dicas Importantes

1. **Sempre marcar a tabela COMPLETA** - incluindo cabeçalho
2. **Salvar frequentemente** - o JSON é atualizado a cada salvamento
3. **Verificar dados extraídos** - conferir com PDF original
4. **Uma categoria por página** - se mudar categoria, é outra página
5. **Nomes de itens únicos** - não repetir nome na mesma página

---

## Troubleshooting

### Marcador não abre
```bash
# Verificar se as imagens foram extraídas
ls extracao_conferencia/pagina_*_original.png
```

### Imagem não carrega
- Verificar se o arquivo existe
- Verificar caminho no código

### Dados incorretos
- Conferir imagem recortada em `recortes/`
- Pedir para Claude reler a imagem

---

## Dependências

```bash
pip install PyMuPDF Pillow pytesseract
```

- **PyMuPDF (fitz)**: Leitura de PDF
- **Pillow (PIL)**: Manipulação de imagens
- **pytesseract**: OCR (opcional, backup)
- **tkinter**: Interface gráfica (vem com Python)

---

---

## RESUMO RÁPIDO (COMANDOS)

```bash
# 1. EXTRAIR PÁGINAS DO PDF (só 1 vez)
python extrair_todas_paginas.py

# 2. ABRIR MARCADOR - usuário marca as áreas
python marcador_catalogo.py

# 3. GERAR RECORTES das áreas marcadas
python extrair_dados.py

# 4. CLAUDE LÊ AS IMAGENS E EXTRAI DADOS
# (Claude adiciona DADOS_PAGINA_X no extrair_dados.py)

# 5. SALVAR DADOS NO JSON
python extrair_dados.py --extrair

# 6. VISUALIZAR DADOS EXTRAÍDOS
python visualizador_dados.py
```

---

## Autor
Pipeline desenvolvido para extração do Catálogo Aluminovo 2025.
Última atualização: Janeiro 2026
