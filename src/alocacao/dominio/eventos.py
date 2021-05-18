from dataclasses import dataclass


class Evento:
    ...


@dataclass
class SemEstoque(Evento):
    sku: str


@dataclass
class Alocado(Evento):
    pedido_id: str
    sku: str
    qtd: int
    ref_lote: str
