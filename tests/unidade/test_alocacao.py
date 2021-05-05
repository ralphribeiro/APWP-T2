from datetime import date, timedelta

from pytest import raises

from src.alocacao.dominio.modelo import Lote, LinhaPedido, alocar, SemEstoque


hoje = date.today()


def test_levantar_exceção_sem_estoque_se_não_puder_alocar():
    sku = 'SANGUE-LATINO'
    lote = Lote('lote-001', sku, 1, eta=None)
    linha = LinhaPedido('pedido-001', sku, 2)

    with raises(SemEstoque):
        alocar(linha, [lote])
