from pytest import mark

from alocacao.camada_servicos import unit_of_work


pytestmark = mark.usefixtures("mappers")

def alocacoes(pedido_id, uow: unit_of_work.SQLAlchemyUOW):
    with uow:
        r = uow.session.execute(
            'SELECT sku, ref_lote FROM alocacoes_view '
            'WHERE pedido_id=:pedido_id',
            dict(pedido_id=pedido_id)
        )
    return [{'sku': sku, 'ref_lote': ref} for sku, ref in r]
