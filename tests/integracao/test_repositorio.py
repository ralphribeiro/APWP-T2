import pytest

from alocacao.dominio import modelo
from alocacao.adapters import repository


pytestmark = pytest.mark.usefixtures("mappers")


def test_obtem_produto_pelo_lore_ref(sqlite_session_factory):
    lote_ref1 = modelo.Lote("lote1", "CELULAR", 10, None)
    lote_ref2 = modelo.Lote("lote2", "CELULAR", 11, None)
    lote_ref3 = modelo.Lote("lote3", "CARREGADOR", 12, None)
    prod1 = modelo.Produto("CELULAR", [lote_ref1, lote_ref2])
    prod2 = modelo.Produto("CARREGADOR", [lote_ref3])

    repo = repository.TrackingRepository(
        repository.SQLAlchemyRepository(sqlite_session_factory())
    )
    repo.get_by_ref(lote_ref2.ref) == prod1
    repo.get_by_ref(lote_ref3.ref) == prod2


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
