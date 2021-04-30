from src.alocacao.dominio import modelo
from src.alocacao.adaptadores import repositorio


def insere_linha_pedido(session):
    session.execute(
        'INSERT INTO linhas_pedido values (pedido_id, sku, qtd) '
        'values ("pedido-001", "TECLADO-RGB", 11)'
    )
    [[id_linha_pedido]] = session.execute(
        'SELECT id FROM linhas_pedido WHERE pedido_id=:pedido_id AND sku=:sku',
        dict(pedido_id='pedido-001', sku='TECLADO-RGB')
    )
    return id_linha_pedido


def insere_lote(session, id_lote):
    session.execute(
        'INSERT INTO lotes (id_lote, sku, _qtd_comprada, eta) '
        'VALUES (:id_l, "TECLADO-RGB", 100, None)',
        dict(id_l=id_lote)
    )

    [[id_lote_]] = session.execute(
        'SELECT id_lote FROM lotes WHERE id_lote=:id_l AND sku=:sku',
        dict(id_l=id_lote, sku='TECLADO-RGB')
    )
    return id_lote_


def insere_alocacao(session, pedido_id, id_lote):
    session.execute(
        'INSERT INTO alocacoes (pedido_id, id_lote) '
        'VALUES (:id_linha, :id_lote)',
        dict(id_linha=pedido_id, id_lote=id_lote)
    )

    [[id_alocacao]] = list(session.execute(
        'SELECT id FROM alocacoes '
        'WHERE pedido_id=:pedido_id AND id_lote=:id_lote',
        dict(pedido_id=pedido_id, id_lote=id_lote)
    ))
    return id_alocacao


def test_repositorio_pode_salvar_um_lote(session):
    lote = modelo.Lote('lote-001', 'COLHER-PEQUENA', 100, eta=None)

    repo = repositorio.SQLAlchemyRepositorio(session)
    repo.insere(lote)
    session.commit()

    linhas = list(session.execute(
        'SELECT ref, sku, _qtd_comprada, eta FROM "lotes"'
    ))

    assert linhas == [('lote-001', 'COLHER-PEQUENA', 100, None)]


def test_repositorio_pode_retornar_um_lote_com_alocacoes(session):
    id_linha = insere_linha_pedido(session)
    id_lote1 = insere_lote(session, 'lote-001')
    insere_lote(session, 'lote-002')
    insere_alocacao(session, id_linha, id_lote1)

    repo = repositorio.SQLAlchemyRepositorio(session)
    retorno = repo.obtem('lote-001')

    esperado = modelo.Lote('lote-001', 'TECLADO-RGB', 100, None)
    assert retorno == esperado
    assert retorno.sku == esperado.sku
    assert retorno._qtd_comprada == esperado._qtd_comprada
    assert retorno._alocacoes == {
        modelo.Lote('lote-001', 'TECLADO-RGB', 11, None)
    }
