import pytest

from alocacao.dominio import modelo
from alocacao.adapters import repository


pytestmark = pytest.mark.usefixtures('mappers')


def insere_linha_pedido(session):
    session.execute(
        'INSERT INTO linhas_pedido (sku, qtd, pedido_id) '
        'VALUES ("TECLADO-RGB", 11, "pedido-001")'
    )
    [[id_linha_pedido]] = session.execute(
        'SELECT id FROM linhas_pedido WHERE pedido_id=:pedido_id AND sku=:sku',
        dict(pedido_id='pedido-001', sku='TECLADO-RGB')
    )
    return id_linha_pedido


def insere_lote(session, id_lote):
    session.execute(
        'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) '
        'VALUES (:id_lote, "TECLADO-RGB", 100, null)',
        dict(id_lote=id_lote)
    )

    [[id_lote_]] = session.execute(
        'SELECT id FROM lotes WHERE ref=:id_lote AND sku=:sku',
        dict(id_lote=id_lote, sku='TECLADO-RGB')
    )
    return id_lote_


def insere_produto(session):
    session.execute(
        'INSERT INTO produtos (sku, versao) '
        'VALUES ("TECLADO-RGB", 0)'
    )


def insere_alocacao(session, id_linha, id_lote):
    session.execute(
        'INSERT INTO alocacoes (pedido_id, lote_id) '
        'VALUES (:id_linha, :id_lote)',
        dict(id_linha=id_linha, id_lote=id_lote)
    )

    [[id_alocacao]] = list(session.execute(
        'SELECT id FROM alocacoes '
        'WHERE pedido_id=:id_linha AND lote_id=:id_lote',
        dict(id_linha=id_linha, id_lote=id_lote)
    ))
    return id_alocacao


def test_repositorio_pode_salvar_um_lote(sqlite_session_factory):
    session = sqlite_session_factory()
    lote = modelo.Lote('lote-001', 'COLHER-PEQUENA', 100, eta=None)

    repo = repository.SQLAlchemyRepository(session)
    repo.add(lote)
    session.commit()

    lotes = list(session.execute(
        'SELECT ref, sku, _qtd_comprada, eta FROM lotes'
    ))
    assert lotes == [('lote-001', 'COLHER-PEQUENA', 100, None)]


def test_repositorio_pode_retornar_um_produto_com_lotes_alocados(sqlite_session_factory):
    session = sqlite_session_factory()
    id_linha = insere_linha_pedido(session)
    id_lote1 = insere_lote(session, 'lote-002')
    insere_produto(session)
    insere_lote(session, 'lote-003')
    id_al = insere_alocacao(session, id_linha, id_lote1)
    assert id_linha

    repo = repository.SQLAlchemyRepository(session)
    retorno_produto = repo.get('TECLADO-RGB')

    esperado = modelo.Lote('lote-002', 'TECLADO-RGB', 100, None)
    assert retorno_produto.lotes[0] == esperado
    assert retorno_produto.sku == esperado.sku
    assert retorno_produto.lotes[0]._qtd_comprada == esperado._qtd_comprada


def test_repositorio_pode_salvar_lote_com_alocacao(sqlite_session_factory):
    session = sqlite_session_factory()
    linha = modelo.LinhaPedido('pedido-005', 'CARREGADOR', 1)
    lote = modelo.Lote('lote-123', 'CARREGADOR', 100, None)
    produto = modelo.Produto('CARREGADOR', [lote])
    produto.alocar(linha)

    repo = repository.SQLAlchemyRepository(session)
    repo.add(produto)
    session.commit()

    [[id_al]] = list(session.execute(
        'SELECT al.id FROM alocacoes AS al '
        'JOIN linhas_pedido AS lp '
        'JOIN lotes AS lt '
        'WHERE al.pedido_id=lp.id '
        'AND al.lote_id=lt.id '
        'AND lp.pedido_id="pedido-005" '
        'AND lp.sku="CARREGADOR" '
        'AND lt.ref="lote-123" '
        'AND lt.sku="CARREGADOR"'
    ))
    assert id_al
