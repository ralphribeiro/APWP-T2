import json

import pytest
from tenacity import Retrying, stop_after_attempt

from . import api_client, redis_client
from ..suporte_testes import(
    id_pedido_aleatorio, sku_aleatorio, ref_lote_aleatorio
)


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
@pytest.mark.usefixtures("restart_redis_pubsub")
def teste_alterar_quantidade_do_lote_levando_a_realocacao():
    pedido_id, sku = id_pedido_aleatorio(), sku_aleatorio()
    lote_antigo_ref = ref_lote_aleatorio('antigo')
    lote_novo_ref = ref_lote_aleatorio('novo')
    api_client.post_insere_lote(lote_antigo_ref, sku, 100, '2021-05-05')
    api_client.post_insere_lote(lote_novo_ref, sku, 100, '2021-05-06')
    resp = api_client.post_aloca(pedido_id, sku, 100)

    assert resp.json()['ref_lote'] == lote_antigo_ref

    subscricao = redis_client.subscribe_to('linha_alocada')

    redis_client.publish_message(
        'altera_quantidade_lote',
        {'ref_lote': lote_antigo_ref, 'qtd_nova': 50}
    )

    mensagens = []
    for attempt in Retrying(stop=stop_after_attempt(3), reraise=True):
        with attempt:
            mensagem = subscricao.get_message(timeout=1)
            if mensagem:
                mensagens.append(mensagem)
            data = json.loads(mensagens[-1]['data'])
            assert data['pedido_id'] == pedido_id
            assert data['ref_lote'] == lote_novo_ref
