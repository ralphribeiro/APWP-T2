from pytest import raises

from src.alocacao.dominio import modelo
from src.alocacao.adaptadores.repositorio import FalsoRepositorio
from src.alocacao.camada_servicos import servicos


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


def test_retorna_alocacoes():
    linha = modelo.LinhaPedido('p1', 'SOUND-BOX', 2)
    lote = modelo.Lote('l1', 'SOUND-BOX', 20, None)
    repo = FalsoRepositorio([lote])
    session = FakeSession()
    resultado = servicos.alocar(linha, repo, session)
    assert resultado == 'l1'


def test_erro_para_sku_invalido():
    linha = modelo.LinhaPedido('p1', 'SKUINEXISTENTE', 2)
    lote = modelo.Lote('l1', 'SOUND-BOX', 20, None)
    repo = FalsoRepositorio([lote])
    session = FakeSession()
    with raises(servicos.SkuInvalido, match='Sku inválido SKUINEXISTENTE'):
        servicos.alocar(linha, repo, session)


def test_commits():
    linha = modelo.LinhaPedido('p1', 'SOUND-BOX', 2)
    lote = modelo.Lote('l1', 'SOUND-BOX', 20, None)
    repo = FalsoRepositorio([lote])
    session = FakeSession()

    servicos.alocar(linha, repo, session)
    assert session.commited
