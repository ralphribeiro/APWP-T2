import requests
from alocacao import config


def post_insere_lote(ref, sku, qtd, eta):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/adiciona_lote",
        json={"ref": ref, "sku": sku, "qtd": qtd, "eta": eta}
    )
    return r


def post_aloca(orderid, sku, qtd, sucesso_esperado=True):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/alocar",
        json={
            "pedido_id": orderid,
            "sku": sku,
            "qtd": qtd,
        },
    )
    if sucesso_esperado:
        assert r.status_code == 201
    return r


def get_alocacao(pedido_id):
    url = config.get_api_url()
    r = requests.get(f"{url}/alocacao/{pedido_id}")
    return r
