from dataclasses import asdict

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


def realocar(
    evento: eventos.Desalocado,
    uow: unit_of_work.SQLAlchemyUOW
):
    with uow:
        produto = uow.produtos.get(sku=evento.sku)
        produto.eventos.append(comandos.Alocar(**asdict(evento)))
        uow.commit()


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


def adiciona_alocacao_ao_modelo_de_leitura(
    evento: eventos.Alocado,
    uow: unit_of_work.SQLAlchemyUOW
):
    with uow:
        uow.session.execute(
            'INSERT INTO alocacoes_view (pedido_id, sku, ref_lote) '
            'VALUES (:pedido_id, :sku, :ref_lote)',
            dict(
                pedido_id=evento.pedido_id,
                sku=evento.sku,
                ref_lote=evento.ref_lote
            )
        )
        uow.commit()


def remove_alocacao_do_modelo_de_leitura(
    evento: eventos.Desalocado,
    uow: unit_of_work.SQLAlchemyUOW
):
    with uow:
        uow.session.execute(
            'DELETE FROM alocacoes_view '
            'WHERE pedido_id=:pedido_id AND sku=:sku',
            dict(pedido_id=evento.pedido_id, sku=evento.sku)
        )
        uow.commit()


EVENT_HANDLERS = {
    eventos.SemEstoque: [envia_notificacao_sem_estoque],
    eventos.Alocado: [
        publica_evento_alocado,
        adiciona_alocacao_ao_modelo_de_leitura
    ],
    eventos.Desalocado: [
        remove_alocacao_do_modelo_de_leitura,
        realocar
    ],
}

COMMAND_HANDLERS = {
    comandos.CriarLote: adiciona_lote,
    comandos.Alocar: alocar,
    comandos.AlterarQuantidadeLote: altera_qtd_lote
}
