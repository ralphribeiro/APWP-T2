from alocacao.adapters import email
from alocacao.aplicacao import redis_eventpublisher
from alocacao.camada_servicos import unit_of_work
from alocacao.dominio import modelo, eventos, comandos


class SkuInvalido(Exception):
    ...


def adiciona_lote(
    comando: comandos.CriarLote,
    uow: unit_of_work.AbstractUOW
):
    with uow:
        produto = uow.produtos.get(sku=comando.sku)
        if produto is None:
            produto = modelo.Produto(comando.sku, lotes=[])
            uow.produtos.add(produto)
        produto.lotes.append(modelo.Lote(
            comando.ref, comando.sku, comando.qtd, comando.eta
        ))
        uow.commit()


def alocar(
    comando: comandos.Alocar,
    uow: unit_of_work.AbstractUOW
) -> str:
    linha = modelo.LinhaPedido(comando.pedido_id, comando.sku, comando.qtd)
    with uow:
        produto = uow.produtos.get(sku=comando.sku)
        if produto is None:
            raise SkuInvalido(f'Sku inválido {comando.sku}')
        ref_lote = produto.alocar(linha)
        uow.commit()
    return ref_lote


def altera_qtd_lote(
    comando: comandos.AlterarQuantidadeLote,
    uow: unit_of_work.AbstractUOW
):
    with uow:
        produto = uow.produtos.get_by_ref(comando.ref)
        produto.altera_qtd_lote(comando.ref, comando.qtd_nova)
        uow.commit()


def envia_notificacao_sem_estoque(
    evento: eventos.SemEstoque,
    uow: unit_of_work.AbstractUOW
):
    email.send_mail(
        'estoque@apwp-t2.com',
        f'Fora de estoque for {evento.sku}'
    )


def publica_evento_alocado(
    evento: eventos.Alocado,
    uow: unit_of_work.AbstractUOW
):
    redis_eventpublisher.publish('linha_alocada', evento)
