import pytest

from alocacao.dominio import modelo

pytestmark = pytest.mark.usefixtures('mappers')


def test_mapeador_linhapedido_pode_carregar_linhas(sqlite_session_factory):
    session = sqlite_session_factory()
    session.execute(
        'INSERT INTO linhas_pedido (pedido_id, sku, qtd) VALUES '
        '("pedido1", "CADEIRA-VERMELHA", 12),'
        '("pedido2", "MESA-ROSA", 13),'
        '("pedido3", "RABO-DE-SETA", 66)'
    )
    esperado = [
        modelo.LinhaPedido("pedido1", "CADEIRA-VERMELHA", 12),
        modelo.LinhaPedido("pedido2", "MESA-ROSA", 13),
        modelo.LinhaPedido("pedido3", "RABO-DE-SETA", 66)
    ]

    assert esperado == session.query(modelo.LinhaPedido).all()


def test_mapeador_linhapedido_pode_salvar_linhas(sqlite_session_factory):
    session = sqlite_session_factory()
    nova_linha = modelo.LinhaPedido('pedido1', 'CASA-DO-CHAPEU', 2)
    session.add(nova_linha)
    session.commit()

    esperado = list(session.execute(
        'SELECT pedido_id, sku, qtd FROM linhas_pedido'
    ))
    assert esperado == [('pedido1', 'CASA-DO-CHAPEU', 2)]


def test_mapeador_lote_pode_carregar_lotes(sqlite_session_factory):
    session = sqlite_session_factory()
    session.execute(
        'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) '
        'values ("lote-111", "CHICLETE-PROHK", 100, null)'
    )
    session.execute(
        'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) '
        'values ("lote-112", "CHICLETE-PROHK", 101, null)'
    )

    esperado = [
        modelo.Lote("lote-111", "CHICLETE-PROHK", 100, None),
        modelo.Lote("lote-112", "CHICLETE-PROHK", 101, None)
    ]
    assert esperado == session.query(modelo.Lote).all()


def test_mapeador_lote_pode_salvar_lotes(sqlite_session_factory):
    session = sqlite_session_factory()
    lote = modelo.Lote('lote-666', 'CORAÇÃO-BALÃO', 1000, None)
    session.add(lote)
    session.commit()

    esperado = list(session.execute(
        'SELECT ref, sku, _qtd_comprada, eta FROM lotes'
    ))
    assert esperado == [('lote-666', 'CORAÇÃO-BALÃO', 1000, None)]


def test_mapeador_alocacao_deve_carregar_alocacoes(sqlite_session_factory):
    session = sqlite_session_factory()
    session.execute(
        'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) VALUES '
        ' ("lote-111", "CADEIRA-VERMELHA", 100, null)'
    )
    session.execute(
        'INSERT INTO linhas_pedido (pedido_id, sku, qtd) VALUES '
        '("pedido1", "CADEIRA-VERMELHA", 10)'
    )
    [[lote_id]] = session.execute(
        'SELECT id FROM lotes WHERE ref="lote-111" '
        'AND sku="CADEIRA-VERMELHA"'
    )
    assert lote_id
    [[pedido_id]] = session.execute(
        'SELECT id FROM linhas_pedido WHERE pedido_id="pedido1" '
        'AND sku="CADEIRA-VERMELHA"'
    )
    assert pedido_id
    session.execute(
        'INSERT INTO alocacoes (pedido_id, lote_id) '
        'VALUES (:pedido_id, :lote_id)',
        dict(pedido_id=pedido_id, lote_id=lote_id)
    )

    lote = session.query(modelo.Lote).one()
    assert lote._alocacoes == {modelo.LinhaPedido(
        'pedido1', 'CADEIRA-VERMELHA', 10)}


def test_mapeador_alocacao_pode_salvar_alocacao(sqlite_session_factory):
    session = sqlite_session_factory()
    linha = modelo.LinhaPedido('pedido2', 'BOLA', 1)
    lote = modelo.Lote('lote2', 'BOLA', 66, None)
    produto = modelo.Produto('BOLA', [lote])
    produto.alocar(linha)
    session.add(lote)
    session.commit()

    [[id_al]] = session.execute(
        'SELECT al.id FROM alocacoes AS al '
        'JOIN lotes as lt '
        'JOIN linhas_pedido AS lp '
        'ON al.lote_id = lt.id '
        'AND al.pedido_id = lp.id '
        'WHERE lt.ref = "lote2" '
        'AND lp.pedido_id = "pedido2" '
        'AND lp.sku = "BOLA"'
    )
    assert id_al
