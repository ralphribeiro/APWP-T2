from datetime import date, timedelta
from src.alocacao.camada_servicos import servicos
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
def test_api_retorna_201_quando_adiciona_um_lote():
    ref = ref_lote_aleatorio()
    sku = sku_aleatorio()
    qtd = 10
    dados = {'ref': ref, 'sku': sku, 'qtd': qtd, 'eta': None}

    url = config.get_api_url()
    resp = requests.post(f'{url}/adiciona_lote', json=dados)

    assert resp.status_code == 201


@pytest.mark.usefixtures('restart_api')
def test_caminho_feliz_api_retorna_201_e_lotes_alocados():
    sku, outro_sku = sku_aleatorio(), sku_aleatorio('outro')

    hoje = date.today().isoformat()
    ontem = date.today().isoformat()

    lote_antigo = {
        'ref': ref_lote_aleatorio(),
        'sku': sku,
        'qtd': 50,
        'eta': ontem,
    }

    lote_atual = {
        'ref': ref_lote_aleatorio(),
        'sku': sku,
        'qtd': 50,
        'eta': hoje,
    }

    _outro_lote = {
        'ref': ref_lote_aleatorio(),
        'sku': outro_sku,
        'qtd': 50,
        'eta': None,
    }

    url = config.get_api_url()

    requests.post(f'{url}/adiciona_lote', json=lote_antigo)
    requests.post(f'{url}/adiciona_lote', json=lote_atual)
    requests.post(f'{url}/adiciona_lote', json=_outro_lote)

    dados = {'pedido_id': id_pedido_aleatorio(), 'sku': sku, 'qtd': 3}
    resp = requests.post(f'{url}/alocar', json=dados)
    assert 200 <= resp.status_code < 300
    assert resp.json()['ref_lote'] == lote_antigo['ref']


@pytest.mark.usefixtures('postgres_db')
@ pytest.mark.usefixtures('restart_api')
def test_path_errado_retorna_mensagem_de_erro_e_400():
    sku_desconhecido, pedido_id = sku_aleatorio(), id_pedido_aleatorio()
    dados = {'pedido_id': pedido_id, 'sku': sku_desconhecido, 'qtd': 15}
    url = config.get_api_url()
    resp = requests.post(f'{url}/alocar', json=dados)
    assert resp.status_code == 400
    assert resp.json()['message'] == f'Sku inválido {sku_desconhecido}'
