from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class LinhaPedido:
    id_perdido: str
    sku: str
    qtd: int


class Lote:
    def __init__(
        self, ref: str,
        sku: str,
        qtd: int,
        eta: Optional[date]
    ):
        self.ref = ref
        self.sku = sku
        self.eta = eta
        self._qtd_comprada = qtd
        self._alocacoes: set[LinhaPedido] = set()

    def alocar(self, linha: LinhaPedido):
        if self.pode_alocar(linha):
            self._alocacoes.add(linha)

    def desalocar(self, linha: LinhaPedido):
        self._alocacoes.discard(linha)

    def pode_alocar(self, linha: LinhaPedido):
        return (
            self.sku == linha.sku and self._qtd_comprada >= linha.qtd
        )

    @property
    def quantidade_alocada(self):
        return sum(linha.qtd for linha in self._alocacoes)

    @property
    def quantidade_disponivel(self):
        return self._qtd_comprada - self.quantidade_alocada
