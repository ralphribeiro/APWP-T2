from datetime import date
from typing import Optional

from src.alocacao.dominio import modelo
from src.alocacao.dominio.modelo import LinhaPedido
from src.alocacao.adaptadores.repositorio import RepositorioAbstrato


class SkuInvalido(Exception):
    ...


def adiciona_lote(
    lote_ref: str,
    sku: str,
    qtd: int,
    eta: Optional[date],
    repo: RepositorioAbstrato,
    session
):
    lote = modelo.Lote(lote_ref, sku, qtd, eta)
    repo.add(lote)
    session.commit()


def sku_valido(sku, lotes) -> bool:
    return sku in {lote.sku for lote in lotes}


def alocar(
    pedido_id: str,
    sku: str,
    qtd: int,
    repo: RepositorioAbstrato,
    session
) -> str:
    lotes = repo.list_all()
    if not sku_valido(sku, lotes):
        raise SkuInvalido(f'Sku inválido {sku}')
    linha = modelo.LinhaPedido(pedido_id, sku, qtd)
    ref_lote = modelo.alocar(linha, lotes)
    session.commit()
    return ref_lote
