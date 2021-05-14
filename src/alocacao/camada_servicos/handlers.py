from datetime import date
from typing import Optional

from alocacao.dominio import modelo, eventos
from alocacao.camada_servicos import unit_of_work
from alocacao.adapters import email

class SkuInvalido(Exception):
    ...


def adiciona_lote(
    evento: eventos.LoteCriado,
    uow: unit_of_work.AbstractUOW
):
    with uow:
        produto = uow.produtos.get(sku=evento.sku)
        if produto is None:
            produto = modelo.Produto(evento.sku, lotes=[])
            uow.produtos.add(produto)
        produto.lotes.append(modelo.Lote(
            evento.ref, evento.sku, evento.qtd, evento.eta
        ))
        uow.commit()


def alocar(
    evento: eventos.AlocacaoRequerida,
    uow: unit_of_work.AbstractUOW
) -> str:
    linha = modelo.LinhaPedido(evento.pedido_id, evento.sku, evento.qtd)
    with uow:
        produto = uow.produtos.get(sku=evento.sku)
        if produto is None:
            raise SkuInvalido(f'Sku inválido {evento.sku}')
        ref_lote = produto.alocar(linha)
        uow.commit()
    return ref_lote


def envia_notificacao_sem_estoque(
    evento: eventos.SemEstoque,
    uow: unit_of_work.AbstractUOW
):
    email.send_mail(
        'estoque@apwp-t2.com',
        f'Fora de estoque for {evento.sku}'
    )

def altera_qtd_lote(
    evento: eventos.AlteradaQuantidadeLote,
    uow: unit_of_work.AbstractUOW
):
    with uow:
        produto = uow.produtos.get_by_ref(evento.ref)
        produto.altera_qtd_lote(evento.ref, evento.qtd_nova)
        uow.commit()
