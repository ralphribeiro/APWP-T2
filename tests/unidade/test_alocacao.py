from datetime import date, timedelta

from pytest import raises

from alocacao.dominio.modelo import Lote, LinhaPedido, Produto, SemEstoque


hoje = date.today()


def test_levantar_exceção_sem_estoque_se_não_puder_alocar():
    sku = 'SANGUE-LATINO'
    lote = Lote('lote-001', sku, 1, eta=None)
    linha = LinhaPedido('pedido-001', sku, 2)

    produto = Produto(sku, [lote])
    with raises(SemEstoque):
        produto.alocar(linha)
