from dataclasses import dataclass
from datetime import date
from typing import Optional


class Evento:
    ...


@dataclass
class SemEstoque(Evento):
    sku: str


@dataclass
class LoteCriado(Evento):
    ref: str
    sku: str
    qtd: int
    eta: Optional[date] = None


@dataclass
class AlocacaoRequerida(Evento):
    pedido_id: str
    sku: str
    qtd: int


@dataclass
class AlteradaQuantidadeLote(Evento):
    ref: str
    qtd_nova: int
