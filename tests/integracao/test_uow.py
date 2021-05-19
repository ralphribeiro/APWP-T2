import threading
from time import sleep
import traceback

from pytest import raises, mark

from ..suporte_testes import(
    id_pedido_aleatorio, ref_lote_aleatorio, sku_aleatorio
)
from alocacao.camada_servicos import unit_of_work
from alocacao.dominio import modelo

pytestmark = mark.usefixtures("mappers")


def insere_lote(session, ref, sku, qtd, eta, versao_produto=0):
    session.execute(
        "INSERT INTO produtos (sku, versao) VALUES (:sku, :versao)",
        dict(sku=sku, versao=versao_produto),
    )
    session.execute(
        "INSERT INTO lotes (ref, sku, _qtd_comprada, eta) "
        "VALUES (:ref, :sku, :qtd, :eta)",
        dict(ref=ref, sku=sku, qtd=qtd, eta=eta),
    )


def obtem_ref_lote_alocado(session, pedido_id, sku):
    [[linha_pedido_id]] = session.execute(
        "SELECT id FROM linhas_pedido WHERE pedido_id=:pedido_id AND sku=:sku",
        dict(pedido_id=pedido_id, sku=sku),
    )
    [[lote_ref]] = session.execute(
        "SELECT lt.ref FROM lotes AS lt "
        "JOIN alocacoes AS al "
        "ON al.lote_id = lt.id "
        "WHERE al.pedido_id=:linha_pedido_id",
        dict(linha_pedido_id=linha_pedido_id),
    )
    return lote_ref


def test_rolls_back_por_padrao_em_um_uow_sem_commit(sqlite_session_factory):
    uow = unit_of_work.SQLAlchemyUOW(sqlite_session_factory)
    with uow:
        insere_lote(uow.session, "lote-00", "MOUSE", 10, None)

    new_session = sqlite_session_factory()

    lotes = list(new_session.execute("SELECT * FROM lotes"))
    assert lotes == []


def test_rolls_back_no_erro(sqlite_session_factory):
    class ExceptionTest(Exception):
        ...

    uow = unit_of_work.SQLAlchemyUOW(sqlite_session_factory)
    with raises(ExceptionTest):
        with uow:
            insere_lote(uow.session, "lote-11", "TECLADO", 12, None)
            raise ExceptionTest()

    lotes = list(uow.session.execute("SELECT * FROM lotes"))
    assert lotes == []


def tenta_alocar(pedido_id, sku, exceptions):
    linha = modelo.LinhaPedido(pedido_id, sku, 10)
    try:
        with unit_of_work.SQLAlchemyUOW() as uow:
            produto = uow.produtos.get(sku)
            produto.alocar(linha)
            sleep(0.2)
            uow.commit()
    except Exception as e:
        # print(traceback.format_exc())
        exceptions.append(e)


def test_atualização_concorrente_para_versao_nao_concorrente(postgres_session_factory):
    sku, lote_ref = sku_aleatorio(), ref_lote_aleatorio()
    session = postgres_session_factory()
    insere_lote(session, lote_ref, sku, 100, None, versao_produto=1)
    session.commit()

    linha_pedido1, linha_pedido2 = id_pedido_aleatorio(), id_pedido_aleatorio()
    exceptions = []
    tenta_alocar_linha1 = lambda: tenta_alocar(linha_pedido1, sku, exceptions)
    tenta_alocar_linha2 = lambda: tenta_alocar(linha_pedido2, sku, exceptions)
    thread1 = threading.Thread(target=tenta_alocar_linha1)
    thread2 = threading.Thread(target=tenta_alocar_linha2)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    [[versao]] = session.execute(
        "SELECT versao FROM produtos WHERE sku=:sku", dict(sku=sku)
    )
    assert versao == 2
    assert "could not serialize access due to concurrent update" in str(exceptions)

    pedidos_ids = list(
        session.execute(
            "SELECT al.pedido_id "
            "FROM alocacoes AS al "
            "JOIN lotes AS lt "
            "ON al.lote_id = lt.id "
            "JOIN linhas_pedido AS lp "
            "ON al.pedido_id = lp.id "
            "WHERE lt.ref=:ref",
            dict(ref=lote_ref),
        )
    )

    assert len(pedidos_ids) == 1

    with unit_of_work.SQLAlchemyUOW(postgres_session_factory) as uow:
        uow.session.execute("SELECT 1")


def test_ao_alocar_versao_deve_ser_incrementada(sqlite_session_factory):
    session = sqlite_session_factory()
    sku = "ROBIN-HOOD"
    insere_lote(session, "lote-inc", sku, 66, None, versao_produto=5)
    linha = modelo.LinhaPedido("pedido-inc", sku, 11)
    with unit_of_work.SQLAlchemyUOW(sqlite_session_factory) as uow:
        produto = uow.produtos.get(sku)
        produto.alocar(linha)
        uow.commit()

    [[versao]] = session.execute(
        "SELECT versao FROM produtos " "WHERE sku=:sku", dict(sku=sku)
    )

    assert versao == 6
