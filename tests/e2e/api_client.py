import requests
from alocacao import config


def post_insere_lote(ref, sku, qtd, eta):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/adiciona_lote",
        json={"ref": ref, "sku": sku, "qtd": qtd, "eta": eta}
    )
    assert r.status_code == 201


def post_aloca(orderid, sku, qty, sucesso_esperado=True):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/alocar",
        json={
            "pedido_id": orderid,
            "sku": sku,
            "qty": qty,
        },
    )
    if sucesso_esperado:
        assert r.status_code == 201
    return r
