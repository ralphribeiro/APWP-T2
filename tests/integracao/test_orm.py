from src.alocacao.dominio import modelo


def test_mapeador_linhapedido_pode_carregar_linhas(session):
    session.execute(
        "INSERT INTO linhas_pedido (pedido_id, sku, qtd) VALUES "
        '("pedido1", "CADEIRA-VERMELHA", 12),'
        '("pedido2", "MESA-ROSA", 13),'
        '("pedido3", "RABO-DE-SETA", 66)'
    )
    esperado = [
        modelo.LinhaPedido("pedido1", "CADEIRA-VERMELHA", 12),
        modelo.LinhaPedido("pedido2", "MESA-ROSA", 13),
        modelo.LinhaPedido("pedido3", "RABO-DE-SETA", 66)
    ]
    session.commit()

    assert esperado == session.query(modelo.LinhaPedido).all()


def test_mapeador_linhapedido_pode_salvar_linhas(session):
    nova_linha = modelo.LinhaPedido('pedido1', 'CASA-DO-CHAPEU', 2)
    session.add(nova_linha)
    session.commit()

    esperado = list(session.execute(
        'SELECT pedido_id, sku, qtd FROM linhas_pedido'
    ))
    assert esperado == [('pedido1', 'CASA-DO-CHAPEU', 2)]


def test_mapeador_lote_pode_carregar_lotes(session):
    session.execute(
        'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) '
        'values ("lote-111", "CHICLETE-PROHK", 100, null)'
    )
    session.execute(
        'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) '
        'values ("lote-112", "CHICLETE-PROHK", 101, null)'
    )
    session.commit()

    esperado = [
        modelo.Lote("lote-111", "CHICLETE-PROHK", 100, None),
        modelo.Lote("lote-112", "CHICLETE-PROHK", 101, None)
    ]

    assert esperado == session.query(modelo.Lote).all()
