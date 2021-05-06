from datetime import date, timedelta

from pytest import raises

from src.alocacao.adapters import repository
from src.alocacao.camada_servicos import servicos, uow


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


class FakeUOW(uow.AbstractUOW):
    def __init__(self):
        self.lotes = repository.FakeRepository()
        self.commited = False

    def commit(self):
        self.commited = True

    def rollback(self):
        ...


def obtem_data(arg: str):
    param = {'ontem': -1, 'hoje': 0, 'amanha': 1}
    return date.today() + timedelta(days=param[arg])


def test_adiciona_lote():
    lote_ref = 'lll-000'
    sku = 'RELOGIO_INTELIGENTE-QUEBRADO'
    qtd = 100
    eta = obtem_data('ontem')

    uow = FakeUOW()

    servicos.adiciona_lote(lote_ref, sku, qtd, eta, uow)
    lote_esperado = uow.lotes.get(lote_ref)
    assert lote_esperado.ref == lote_ref


def test_commits():
    lote = ('l1', 'SOUND-BOX', 20, None)
    uow = FakeUOW()
    servicos.adiciona_lote(*lote, uow)
    servicos.alocar('p1', 'SOUND-BOX', 2, uow)
    assert uow.commited


def test_retorna_ref_lote_ao_alocar_com_sucesso():
    lote = ('l1', 'SOUND-BOX', 20, None)
    uow = FakeUOW()
    servicos.adiciona_lote(*lote, uow)
    resultado = servicos.alocar('p1', 'SOUND-BOX', 2, uow)
    assert resultado == 'l1'


def test_erro_para_sku_invalido():
    lote = ('l1', 'SOUND-BOX', 20, None)

    uow = FakeUOW()

    servicos.adiciona_lote(*lote, uow)
    with raises(servicos.SkuInvalido, match='Sku inválido SKUINEXISTENTE'):
        servicos.alocar('p1', 'SKUINEXISTENTE', 2, uow)


def test_preferir_estoque_local_ao_em_transporte():
    lote_hoje = ('lote-99', 'VASSOURA-E-RODO', 50, obtem_data('hoje'))
    lote_amanha = ('lote-100', 'VASSOURA-E-RODO', 44, obtem_data('amanha'))

    uow = FakeUOW()

    servicos.adiciona_lote(*lote_hoje, uow)
    servicos.adiciona_lote(*lote_amanha, uow)

    servicos.alocar('p1', 'VASSOURA-E-RODO', 2, uow)
    servicos.alocar('p2', 'VASSOURA-E-RODO', 3, uow)

    esperdo_lote_hoje = uow.lotes.get(lote_hoje[0])
    esperdo_lote_amanha = uow.lotes.get(lote_amanha[0])

    assert esperdo_lote_hoje.quantidade_disponivel == 45
    assert esperdo_lote_amanha.quantidade_disponivel == 44


def test_retorna_referencia_do_lote_alocado():
    sku = 'GUARIROBA-GIGANTE'
    lote_em_estoque = ('lote-001', sku, 10, None)
    lote_em_chegando = ('lote-002', sku, 10, obtem_data('amanha'))
    linha = ('pedido-001', sku, 5)

    uow = FakeUOW()

    servicos.adiciona_lote(*lote_em_estoque, uow)
    servicos.adiciona_lote(*lote_em_chegando, uow)

    esperado = servicos.alocar(*linha, uow)

    assert esperado == 'lote-001'


def test_preferir_lote_mais_antigo():
    sku = 'GARRAFA-VAZIA'
    lote_antigo = ('lote-antigo', sku, 20, obtem_data('ontem'))
    lote_atual = ('lote-atual', sku, 10, obtem_data('hoje'))
    lote_futuro = ('lote-futuro', sku, 30, obtem_data('amanha'))
    linha = ('pedido-001', sku, 5)

    uow = FakeUOW()

    servicos.adiciona_lote(*lote_antigo, uow)
    servicos.adiciona_lote(*lote_atual, uow)
    servicos.adiciona_lote(*lote_futuro, uow)
    servicos.alocar(*linha, uow)

    esperado_lote_antigo = uow.lotes.get(lote_antigo[0])
    esperado_lote_atual = uow.lotes.get(lote_atual[0])
    esperado_lote_futuro = uow.lotes.get(lote_futuro[0])

    assert esperado_lote_antigo.quantidade_disponivel == 15
    assert esperado_lote_atual.quantidade_disponivel == 10
    assert esperado_lote_futuro.quantidade_disponivel == 30
