from dataclasses import dataclass


class Evento:
    ...


@dataclass
class SemEstoque(Evento):
    sku: str
