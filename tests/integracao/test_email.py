import requests
from sqlalchemy.orm import clear_mappers

from alocacao import bootstrap, config
from alocacao.adapters import notifications
from alocacao.camada_servicos import unit_of_work
from alocacao.dominio import comandos

from ..suporte_testes import sku_aleatorio

import pytest


@pytest.fixture
def bus(sqlite_session_factory):
    bus = bootstrap.bootstrap(
        start_orm=True,
        uow=unit_of_work.SQLAlchemyUOW(sqlite_session_factory),
        notifications=notifications.EmailNotifications(),
        publish=lambda *args: None,
    )
    yield bus
    clear_mappers()


def get_email_from_mailhog(sku):
    host, port = map(config.get_email_host_and_port().get,
                     ['host', 'http_port'])
    all_emails = requests.get(f'http://{host}:{port}/api/v2/messages').json()
    return next((m for m in all_emails['items'] if sku in str(m)), 0)


def test_out_of_stock_email(bus):
    sku = sku_aleatorio()
    bus.handle(comandos.CriarLote('lote121', sku, 11, None))
    bus.handle(comandos.Alocar('pedido121', sku, 12))
    email = get_email_from_mailhog(sku)
    assert email['Raw']['From'] == 'alocacoes@apwp-t2.com'        # type: ignore
    assert email['Raw']['To'] == ['estoque@apwp-t2.com']          # type: ignore
    assert f'Fora de estoque para {sku}' in email['Raw']['Data']  # type: ignore
