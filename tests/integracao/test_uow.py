from src.alocacao.adapters import repository, uow


def insere_lote(session, ref, sku, qtd, eta):
    session.execute(
        'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) '
        'VALUES (:ref, :sku, :qtd, :eta)',
        dict(ref=ref, sku=sku, qtd=qtd, eta=eta)
    )


# def insere_linhas(session, pedido_id, sku, qtd):
#     session.execute(
#         'INSERT INTO linhas_pedido (pedido_id, sku, qtd) '
#         'VALUES (:pedido_id, :sku, :qtd)',
#         dict(pedido_id=pedido_id, sku=sku, qtd=qtd)
#     )


def ref_lote_alocado(session, pedido_id, sku):
    [[linha_pedido_id]] = session.execute(
        'SELECT id FROM linhas_pedido '
        'WHERE pedido_id=:pedido_id '
        'AND sku=:sku',
        dict(pedido_id=pedido_id, sku=sku)
    )
    [[lote_ref]] = session.execute(
        'SELECT lt.ref FROM lotes AS lt '
        'JOIN alocacoes AS al '
        'ON al.lote_id = lt.id'
        'WHERE al.pedido_id=:linha_pedido_id',
        dict(linha_pedido_id=linha_pedido_id)
    )
    return lote_ref

# def test_uow_pode_retornar_lote(session):
#     insere_lote(session)