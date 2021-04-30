from datetime import date, timedelta

from pytest import raises

from src.alocacao.dominio.modelo import Lote, LinhaPedido, alocar, SemEstoque

hoje = date.today()


def test_preferir_estoque_atual_a_remessas():
    sku = 'TOALHA-ROSTO'
    lote_local = Lote('lote-001', sku, 20, eta=None)
    lote_futuro = Lote('lote-002', sku, 10, eta=hoje+timedelta(days=2))
    linha = LinhaPedido('pedido-001', sku, 5)
    alocar(linha, [lote_local, lote_futuro])
    assert lote_local.quantidade_disponivel == 15
    assert lote_futuro.quantidade_disponivel == 10


def test_preferir_lote_mais_antigo():
    sku = 'GARRAFA-VAZIA'
    lote_antigo = Lote('lote-antigo', sku, 20, eta=hoje-timedelta(days=10))
    lote_atual = Lote('lote-atual', sku, 10, eta=hoje)
    lote_futuro = Lote('lote-futuro', sku, 30, eta=hoje+timedelta(days=5))
    linha = LinhaPedido('pedido-001', sku, 5)
    alocar(linha, [lote_antigo, lote_atual, lote_futuro])
    assert lote_antigo.quantidade_disponivel == 15
    assert lote_atual.quantidade_disponivel == 10
    assert lote_futuro.quantidade_disponivel == 30


def test_retorna_referencia_do_lote_alocado():
    sku = 'GUARIROBA-GIGANTE'
    lote_em_estoque = Lote('lote-001', sku, 10, eta=None)
    lote_em_chegando = Lote('lote-002', sku, 10, eta=hoje+timedelta(2))
    linha = LinhaPedido('pedido-001', sku, 5)
    assert alocar(linha, [lote_em_estoque, lote_em_chegando]) == 'lote-001'


def test_levantar_exceção_sem_estoque_se_não_puder_alocar():
    sku = 'SANGUE-LATINO'
    lote = Lote('lote-001', sku, 1, eta=None)
    linha = LinhaPedido('pedido-001', sku, 2)

    with raises(SemEstoque):
        alocar(linha, [lote])
