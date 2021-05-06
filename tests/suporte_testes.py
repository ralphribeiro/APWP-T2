from uuid import uuid4


def sufixo_aleatorio():
    return uuid4().hex[:6]


def sku_aleatorio(sufixo=None):
    return f'{sufixo}-{sufixo_aleatorio()}'


def ref_lote_aleatorio(sufixo=None):
    return f'{sufixo}-{sufixo_aleatorio()}'


def id_pedido_aleatorio(sufixo=None):
    return f'{sufixo}-{sufixo_aleatorio()}'
