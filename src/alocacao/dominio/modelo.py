from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional


class SemEstoque(Exception):
    ...


class Produto:
    def __init__(self, sku, lotes: list[Lote], versao: int = 0):
        self.sku = sku
        self.lotes = lotes
        self.versao = versao

    def alocar(self, linha: LinhaPedido) -> str:
        try:
            lote = next(
                l for l in sorted(self.lotes) if l.pode_alocar(linha)
            )
        except StopIteration:
            raise SemEstoque(f'Sem estoque para sku: {linha.sku}')
        else:
            lote.alocar(linha)
            self.versao += 1

        return lote.ref


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

    def __repr__(self) -> str:
        return f'<lote {self.ref}>'

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

    def __hash__(self) -> int:
        return hash(self.ref)

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
