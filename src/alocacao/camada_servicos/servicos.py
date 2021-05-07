from datetime import date
from typing import Optional

from src.alocacao.dominio import modelo
from src.alocacao.camada_servicos import unit_of_work


class SkuInvalido(Exception):
    ...


def adiciona_lote(
    lote_ref: str,
    sku: str,
    qtd: int,
    eta: Optional[date],
    uow: unit_of_work.AbstractUOW
):
    with uow:
        produto = uow.produtos.get(sku)
        if produto is None:
            produto = modelo.Produto(sku, lotes=[])
            uow.produtos.add(produto)
        produto.lotes.append(modelo.Lote(lote_ref, sku, qtd, eta))
        uow.commit()


def alocar(
    pedido_id: str,
    sku: str,
    qtd: int,
    uow: unit_of_work.AbstractUOW
) -> str:
    linha = modelo.LinhaPedido(pedido_id, sku, qtd)
    with uow:
        produto = uow.produtos.get(sku=sku)
        if produto is None:
            raise SkuInvalido(f'Sku inválido {sku}')
        ref_lote = produto.alocar(linha)
        uow.commit()
    return ref_lote
