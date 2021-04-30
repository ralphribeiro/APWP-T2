from dataclasses import dataclass
from datetime import date
from typing import Optional


class SemEstoque(Exception):
    ...


@dataclass(unsafe_hash=True)
class LinhaPedido:
    pedido_id: str
    sku: str
    qtd: int


class Lote:
    def __init__(
        self,
        ref: str,
        sku: str,
        qtd: int,
        eta: Optional[date]
    ):
        self.ref = ref
        self.sku = sku
        self.eta = eta
        self._qtd_comprada = qtd
        self._alocacoes: set[LinhaPedido] = set()

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __eq__(self, other) -> bool:
        if not isinstance(other, Lote):
            return False
        return self.ref == other.ref

    def alocar(self, linha: LinhaPedido):
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


def alocar(linha: LinhaPedido, lotes: list[Lote]) -> str:
    try:
        lote = next(l for l in sorted(lotes) if l.pode_alocar(linha))
    except StopIteration:
        raise SemEstoque(f'Sem estoque para sku: {linha.sku}')
    else:
        lote.alocar(linha)

    return lote.ref
