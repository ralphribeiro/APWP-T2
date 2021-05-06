from datetime import date
from typing import Optional

from src.alocacao.dominio import modelo
from src.alocacao.camada_servicos import uow


class SkuInvalido(Exception):
    ...


def adiciona_lote(
    lote_ref: str,
    sku: str,
    qtd: int,
    eta: Optional[date],
    uow: uow.AbstractUOW
):
    lote = modelo.Lote(lote_ref, sku, qtd, eta)
    with uow:
        uow.lotes.add(lote)
        uow.commit()


def sku_valido(sku, lotes) -> bool:
    return sku in {lote.sku for lote in lotes}


def alocar(
    pedido_id: str,
    sku: str,
    qtd: int,
    uow: uow.AbstractUOW
) -> str:
    with uow:
        lotes = uow.lotes.list_all()
        if not sku_valido(sku, lotes):
            raise SkuInvalido(f'Sku inválido {sku}')
        linha = modelo.LinhaPedido(pedido_id, sku, qtd)
        ref_lote = modelo.alocar(linha, lotes)
        uow.commit()
    return ref_lote
