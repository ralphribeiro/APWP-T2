from datetime import date

import pytest

from alocacao import config
from ..suporte_testes import (
    ref_lote_aleatorio, sku_aleatorio, id_pedido_aleatorio
)

from . import api_client


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_caminho_feliz_api_retorna_202_lote_é_alocados():
    sku, outro_sku = sku_aleatorio(), sku_aleatorio('outro')
    hoje = date.today().isoformat()
    ontem = date.today().isoformat()
    ref_lote_antigo = ref_lote_aleatorio()
    ref_lote_atual = ref_lote_aleatorio()
    ref_lote_futuro = ref_lote_aleatorio()
    api_client.post_insere_lote(ref_lote_antigo, sku, 50, ontem)
    api_client.post_insere_lote(ref_lote_atual, sku, 50, hoje)
    api_client.post_insere_lote(ref_lote_futuro, outro_sku, 50, None)

    pedido_id = id_pedido_aleatorio()
    r = api_client.post_aloca(
        pedido_id, sku, 3, sucesso_esperado=False
    )
    assert r.ok

    r = api_client.get_alocacao(pedido_id)
    assert r.json() == [{'sku': sku, 'ref_lote': ref_lote_antigo}]


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_path_errado_retorna_mensagem_de_erro_e_400():
    sku_desconhecido, pedido_id = sku_aleatorio(), id_pedido_aleatorio()
    dados = {'pedido_id': pedido_id, 'sku': sku_desconhecido, 'qtd': 15}
    r = api_client.post_aloca(
        id_pedido_aleatorio(), sku_desconhecido, 3, sucesso_esperado=False
    )
    assert r.status_code == 400
    assert r.json()['message'] == f'Sku inválido {sku_desconhecido}'

    r = api_client.get_alocacao(pedido_id)
    assert r.status_code == 404
