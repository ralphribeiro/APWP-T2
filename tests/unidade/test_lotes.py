from datetime import date

from src.alocacao.dominio.modelo import LinhaPedido, Lote


def faz_lote_e_linha(sku, qtd_lote, qtd_linha):
    lote = Lote('Lote-001', sku, qtd_lote, eta=date.today())
    linha = LinhaPedido('pedido-001', sku, qtd_linha)
    return lote, linha


def test_alocar_para_um_lote_reduz_a_quantidade_disponivel():
    lote, linha = faz_lote_e_linha('MESA-PEQUENA', 20, 2)
    lote.alocar(linha)
    assert lote.quantidade_disponivel == 18


def test_alocar_se_quantidade_disponivel_maior_que_requerida():
    lote_grande, linha_pequena = faz_lote_e_linha('BALA-BORRACHA', 20, 2)
    assert lote_grande.pode_alocar(linha_pequena) is True


def test_nao_alocar_se_quantidade_disponivel_menor_que_requerida():
    lote_grande, linha_pequena = faz_lote_e_linha('BALA-BORRACHA', 2, 20)
    assert lote_grande.pode_alocar(linha_pequena) is False


def test_nao_alocar_se_quantidade_disponivel_igual_requerida():
    lote_grande, linha_pequena = faz_lote_e_linha('BALA-BORRACHA', 2, 2)
    assert lote_grande.pode_alocar(linha_pequena) is True


def test_nao_alocar_se_sku_diferente():
    lote = Lote('Lote-001', 'BALA-BORRACHA', 20, eta=date.today())
    linha = LinhaPedido('Pedido-001', 'BALA-GOMA', 2)
    assert lote.pode_alocar(linha) is False

def test_desalocar_linha_somente_se_alocada():
    lote, linha_a_desalocar = faz_lote_e_linha('BOLA-CRISTAL', 10, 2)
    lote.desalocar(linha_a_desalocar)
    assert lote.quantidade_disponivel == 10

def test_alocacao_idempotente():
    lote, linha = faz_lote_e_linha('BOLA-CRISTAL', 10, 2)
    lote.alocar(linha)
    lote.alocar(linha)
    assert lote.quantidade_alocada == 2
