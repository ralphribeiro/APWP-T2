from datetime import date, timedelta
from uuid import uuid4

import pytest
import requests

from src.alocacao import config


def sufixo_aleatorio():
    return uuid4().hex[:6]


def sku_aleatorio(sufixo=None):
    return f'{sufixo}-{sufixo_aleatorio()}'


def ref_lote_aleatorio(sufixo=None):
    return f'{sufixo}-{sufixo_aleatorio()}'


def id_pedido_aleatorio(sufixo=None):
    return f'{sufixo}-{sufixo_aleatorio()}'


@pytest.mark.usefixtures('restart_api')
def test_api_retorna_201_e_lotes_alocados(add_lote):
    sku, outro_sku = sku_aleatorio(), sku_aleatorio('outro')
    lote_antigo = ref_lote_aleatorio()
    lote_atual = ref_lote_aleatorio()
    outro_lote = ref_lote_aleatorio()

    hoje = date.today()
    add_lote([
        (lote_antigo, sku, 50, hoje-timedelta(days=1)),
        (lote_atual, sku, 50, hoje),
        (outro_lote, outro_sku, 50, None)
    ])
    dados = {'pedido_id': id_pedido_aleatorio(), 'sku': sku, 'qtd': 3}
    url = config.get_api_url()
    resp = requests.post(f'{url}/alocar', json=dados)
    assert resp.status_code == 201
    assert resp.json()['ref_lote'] == lote_antigo


@pytest.mark.usefixtures('restart_api')
def test_path_erado_retorna_mensagem_de_erro_e_400():
    sku_desconhecido, pedido_id = sku_aleatorio(), id_pedido_aleatorio()
    dados = {'pedido_id': pedido_id, 'sku': sku_desconhecido, 'qtd': 15}
    url = config.get_api_url()
    resp = requests.post(f'{url}/alocar', json=dados)
    assert resp.status_code == 400
    assert resp.json()['message'] == f'Sku inválido {sku_desconhecido}'
