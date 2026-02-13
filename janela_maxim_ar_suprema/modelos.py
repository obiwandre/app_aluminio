"""
Modelos de dados para o Visualizador de Janela Maxim-Ar Suprema.
"""
from dataclasses import dataclass, field
from typing import List
from enum import Enum


class TipoSecao(Enum):
    QUADRO = "QUADRO"
    FOLHA = "FOLHA"
    VIDRO = "VIDRO"


class PosicaoPeca(Enum):
    LARGURA_S = "Largura S"
    LARGURA_I = "Largura I"
    ALTURA_E = "Altura E"
    ALTURA_D = "Altura D"


@dataclass
class Peca:
    """Uma peca da esquadria de aluminio."""
    secao: TipoSecao
    posicao: PosicaoPeca
    perfil: str              # "SU079", "SU082", "SU200", "Vidro"
    medida_com: float        # dimensao em mm COM contramarco
    medida_sem: float        # dimensao em mm SEM contramarco
    corte_esq: int           # angulo de corte esquerdo/superior (45 ou 90)
    corte_dir: int           # angulo de corte direito/inferior (45 ou 90)
    desconto_com: float      # constante subtraida (COM)
    desconto_sem: float      # constante subtraida (SEM)
    formula: str             # descricao da formula

    def medida(self, com_contramarco: bool) -> float:
        return self.medida_com if com_contramarco else self.medida_sem


@dataclass
class DadosJanela:
    """Especificacao completa de uma janela Maxim-Ar."""
    largura_vao: float
    altura_vao: float
    pecas_quadro: List[Peca] = field(default_factory=list)
    pecas_folha: List[Peca] = field(default_factory=list)
    pecas_vidro: List[Peca] = field(default_factory=list)

    def todas_pecas(self) -> List[Peca]:
        return self.pecas_quadro + self.pecas_folha + self.pecas_vidro

    def peca_por_posicao(self, secao: TipoSecao, posicao: PosicaoPeca) -> Peca:
        pecas = {
            TipoSecao.QUADRO: self.pecas_quadro,
            TipoSecao.FOLHA: self.pecas_folha,
            TipoSecao.VIDRO: self.pecas_vidro,
        }[secao]
        for p in pecas:
            if p.posicao == posicao:
                return p
        raise ValueError(f"Peca nao encontrada: {secao.value} / {posicao.value}")
