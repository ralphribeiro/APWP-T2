from datetime import date
from dataclasses import dataclass
from typing import Optional


@dataclass
class Comando:
    ...


@dataclass
class Alocar(Comando):
    pedido_id: str
    sku: str
    qtd: int


@dataclass
class CriarLote(Comando):
    ref: str
    sku: str
    qtd: int
    eta: Optional[date] = None


@dataclass
class AlterarQuantidadeLote(Comando):
    ref: str
    qtd_nova: int
