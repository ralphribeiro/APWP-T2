from alocacao.dominio import eventos, modelo


def test_registra_um_evento_fora_de_estoque_quando_nao_for_possivel_alocar():
    lote = modelo.Lote('lote-sem-estoque', 'RELOGIO', 2, None)
    produto = modelo.Produto('RELOGIO', [lote])
    linha = modelo.LinhaPedido('pedido-sem-estoque', 'RELOGIO', 2)
    produto.alocar(linha)

    linha2 = modelo.LinhaPedido('pedido-sem-estoque2', 'RELOGIO', 1)
    alocacao = produto.alocar(linha2)


    assert produto.mensagens[-1] == eventos.SemEstoque(sku='RELOGIO')
    assert alocacao is None
