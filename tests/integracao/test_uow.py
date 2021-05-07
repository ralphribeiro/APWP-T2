from pytest import raises

from tests.conftest import session_factory
from src.alocacao.camada_servicos import unit_of_work
from src.alocacao.dominio import modelo


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


def obtem_ref_lote_alocado(session, pedido_id, sku):
    [[linha_pedido_id]] = session.execute(
        'SELECT id FROM linhas_pedido '
        'WHERE pedido_id=:pedido_id '
        'AND sku=:sku',
        dict(pedido_id=pedido_id, sku=sku)
    )
    [[lote_ref]] = session.execute(
        'SELECT lt.ref FROM lotes AS lt '
        'JOIN alocacoes AS al '
        'ON al.lote_id = lt.id '
        'WHERE al.pedido_id=:linha_pedido_id',
        dict(linha_pedido_id=linha_pedido_id)
    )
    return lote_ref


def test_rolls_back_por_padrao_em_um_uow_sem_commit(session_factory):
    uow = unit_of_work.SQLAlchemyUOW(session_factory)
    with uow:
        insere_lote(uow.session, 'lote-00', 'MOUSE', 10, None)

    new_session = session_factory()

    lotes = list(new_session.execute(
        'SELECT * FROM lotes'
    ))
    assert lotes == []


def test_rolls_back_no_erro(session_factory):
    class ExceptionTest(Exception):
        ...

    uow = unit_of_work.SQLAlchemyUOW(session_factory)
    with raises(ExceptionTest):
        with uow:
            insere_lote(uow.session, 'lote-11', 'TECLADO', 12, None)
            raise ExceptionTest()

    lotes = list(uow.session.execute(
        'SELECT * FROM lotes'
    ))
    assert lotes == []


def test_uow_pode_retornar_um_lote_e_alocá_lo(session_factory):
    session = session_factory()
    insere_lote(session, 'lote-22', 'MONITOR', 12, None)
    session.commit()

    uow = unit_of_work.SQLAlchemyUOW(session_factory)
    with uow:
        lote = uow.lotes.get('lote-22')
        linha = modelo.LinhaPedido('pedido-22', 'MONITOR', 1)
        lote.alocar(linha)
        uow.commit()

    lote_ref = obtem_ref_lote_alocado(session, 'pedido-22', 'MONITOR')
    assert lote_ref == 'lote-22'
