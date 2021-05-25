from datetime import date, timedelta

import pytest
from sqlalchemy.orm import clear_mappers

from alocacao import bootstrap, views
from alocacao.camada_servicos import messagebus, unit_of_work
from alocacao.dominio import comandos


@pytest.fixture
def sqlite_bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=unit_of_work.TrackingUOW(SQLAlchemyUOW(sqlite_session_factory)),
        send_mail=lambda *args: None,
        publish=lambda *args: None
    )
    yield bus
    clear_mappers()


def test_view_alocacoes(sqlite_bus):
    sqlite_bus.handle(comandos.CriarLote(
        'lote1', 'sku1', 10, date.today() - timedelta(days=1)))
    sqlite_bus.handle(comandos.CriarLote(
        'lote2', 'sku2', 10, date.today() + timedelta(days=1)))
    sqlite_bus.handle(comandos.Alocar('pedido1', 'sku1', 5))
    sqlite_bus.handle(comandos.Alocar('pedido1', 'sku2', 5))

    sqlite_bus.handle(comandos.CriarLote(
        'lote3', 'sku3', 10, date.today() - timedelta(days=1)))
    sqlite_bus.handle(comandos.CriarLote(
        'lote4', 'sku4', 10, date.today() + timedelta(days=1)))
    sqlite_bus.handle(comandos.Alocar('pedido2', 'sku3', 5))
    sqlite_bus.handle(comandos.Alocar('pedido2', 'sku4', 5))

    r = views.alocacoes('pedido1', sqlite_bus.uow)
    assert r == [
        {'sku': 'sku1', 'ref_lote': 'lote1'},
        {'sku': 'sku2', 'ref_lote': 'lote2'}
    ]


def test_desalocacoes(sqlite_bus):
    sqlite_bus.handle(comandos.CriarLote(
        'lote1', 'sku1', 10, date.today() - timedelta(days=1)))
    sqlite_bus.handle(comandos.CriarLote(
        'lote2', 'sku1', 10, date.today() + timedelta(days=1)))
    sqlite_bus.handle(comandos.Alocar('pedido1', 'sku1', 5))

    sqlite_bus.handle(comandos.AlterarQuantidadeLote('lote1', 1))

    r = views.alocacoes('pedido1', sqlite_bus.uow)
    assert r == [{'sku': 'sku1', 'ref_lote': 'lote2'}]
