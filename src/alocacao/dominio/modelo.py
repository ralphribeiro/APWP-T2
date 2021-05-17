from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional

from . import eventos


class SemEstoque(Exception):
    ...


class Produto:
    def __init__(self, sku, lotes: list[Lote], versao: int = 0):
        self.sku = sku
        self.lotes = lotes
        self.versao = versao
        self.eventos: list[eventos.Evento] = []

    def alocar(self, linha: LinhaPedido) -> str:
        try:
            lote = next(l for l in sorted(self.lotes) if l.pode_alocar(linha))
        except StopIteration:
            self.eventos.append(eventos.SemEstoque(sku=linha.sku))
            return None
        else:
            lote.alocar(linha)
            self.versao += 1
            return lote.ref

    def altera_qtd_lote(self, ref, qtd_nova):
        lote = next((lt for lt in self.lotes if lt.ref == ref), None)
        lote.altera_qtd(qtd_nova)        
        while qtd_nova > lote.quantidade_disponivel:
            linha = lote.desalocar_um()
            self.eventos.append(eventos.AlocacaoRequerida(
                linha.pedido_id, linha.sku, linha.qtd
            ))
        return lote.ref


@dataclass(unsafe_hash=True)
class LinhaPedido:
    pedido_id: str
    sku: str
    qtd: int


class Lote:
    def __init__(self, ref: str, sku: str, qtd: int, eta: Optional[date]):
        self.ref = ref
        self.sku = sku
        self.eta = eta
        self._qtd_comprada = qtd
        self._alocacoes: set[LinhaPedido] = set()

    def __repr__(self) -> str:
        return f"<lote {self.ref}>"

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
        if self.pode_alocar(linha):
            self._alocacoes.add(linha)

    def desalocar(self, linha: LinhaPedido):
        self._alocacoes.discard(linha)

    def desalocar_um(self) -> LinhaPedido:
        return self._alocacoes.pop()

    def pode_alocar(self, linha: LinhaPedido):
        return self.sku == linha.sku and self.quantidade_disponivel >= linha.qtd

    def altera_qtd(self, qtd_nova):
        self._qtd_comprada = qtd_nova

    @property
    def quantidade_alocada(self):
        return sum(linha.qtd for linha in self._alocacoes)

    @property
    def quantidade_disponivel(self):
        return self._qtd_comprada - self.quantidade_alocada
