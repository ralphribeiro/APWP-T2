from datetime import date, timedelta

import pytest

from alocacao import views
from alocacao.camada_servicos import messagebus, unit_of_work
from alocacao.dominio import comandos


pytestmark = pytest.mark.usefixtures('mappers')


def test_view_alocacoes(sqlite_session_factory):
    uow = unit_of_work.SQLAlchemyUOW(sqlite_session_factory)

    messagebus.handle(comandos.CriarLote(
        'lote1', 'sku1', 10, date.today() - timedelta(days=1)), uow)
    messagebus.handle(comandos.CriarLote(
        'lote2', 'sku2', 10, date.today() + timedelta(days=1)), uow)
    messagebus.handle(comandos.Alocar('pedido1', 'sku1', 5), uow)
    messagebus.handle(comandos.Alocar('pedido1', 'sku2', 5), uow)

    messagebus.handle(comandos.CriarLote(
        'lote3', 'sku3', 10, date.today() - timedelta(days=1)), uow)
    messagebus.handle(comandos.CriarLote(
        'lote4', 'sku4', 10, date.today() + timedelta(days=1)), uow)
    messagebus.handle(comandos.Alocar('pedido2', 'sku3', 5), uow)
    messagebus.handle(comandos.Alocar('pedido2', 'sku4', 5), uow)

    r = views.alocacoes('pedido1', uow)
    assert r == [
        {'sku': 'sku1', 'ref_lote': 'lote1'},
        {'sku': 'sku2', 'ref_lote': 'lote2'}
    ]


def test_desalocacoes(sqlite_session_factory):
    uow = unit_of_work.SQLAlchemyUOW(sqlite_session_factory)

    messagebus.handle(comandos.CriarLote(
        'lote1', 'sku1', 10, date.today() - timedelta(days=1)), uow)
    messagebus.handle(comandos.CriarLote(
        'lote2', 'sku1', 10, date.today() + timedelta(days=1)), uow)
    messagebus.handle(comandos.Alocar('pedido1', 'sku1', 5), uow)

    messagebus.handle(comandos.AlterarQuantidadeLote('lote1', 1), uow)

    r = views.alocacoes('pedido1', uow)
    assert r == [{'sku': 'sku1', 'ref_lote': 'lote2'}]
