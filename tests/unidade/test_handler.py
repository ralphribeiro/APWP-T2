from datetime import date, timedelta
from typing import Union

from pytest import raises

from alocacao.adapters import repository
from alocacao.camada_servicos import handlers, messagebus, unit_of_work
from alocacao.dominio import comandos, eventos, modelo


class FakeSession:
    commited = False

    def commit(self):
        self.commited = True


class FakeRepository():  # adaptador
    def __init__(self):
        super().__init__()
        self._produtos = set()

    def add(self, produto: modelo.Produto):
        self._produtos.add(produto)

    def get(self, sku) -> modelo.Produto:
        return next(
            (produto for produto in self._produtos if produto.sku == sku),
            None
        )

    def get_by_ref(self, lote_ref) -> modelo.Produto:
        return next(
            (p for p in self._produtos for lt in p.lotes if lt.ref == lote_ref),
            None
        )


class FakeUOW(unit_of_work.AbstractUOW):
    def __init__(self):
        self.produtos = repository.TrackingRepository(FakeRepository())
        self.commited = False

    def _commit(self):
        self.commited = True

    def rollback(self):
        ...

class FakeUOWWithFakeMsgBus(FakeUOW):
    def __init__(self):
        super().__init__()
        self.msgs_published: list[Union[eventos.Evento, comandos.Comando]] = []

    def publish_events(self):
        for produto in self.produtos.seen:
            while produto.eventos:
                self.msgs_published.append(produto.eventos.pop(0))


def obtem_data(arg: str):
    param = {'ontem': -1, 'hoje': 0, 'amanha': 1}
    return date.today() + timedelta(days=param[arg])


class TestAdicionaAlocacao:
    def test_para_novo_produto(self):
        uow = FakeUOW()
        messagebus.handle(
            comandos.CriarLote('l-1', 'UHUL', 10, None), uow
        )
        assert uow.produtos.get('UHUL')
        assert uow.commited


class TestAllocate:
    def test_retorna_alocacao(self):
        uow = FakeUOW()
        messagebus.handle(
            comandos.CriarLote('l-2', 'GARRAFA-VAZIA', 54, None), uow
        )
        [resultado] = messagebus.handle(
            comandos.Alocar('p-2', 'GARRAFA-VAZIA', 10), uow
        )
        assert resultado == 'l-2'

    
    def test_para_sku_invalido(self):
        lote = ('l1', 'SOUND-BOX', 20, None)
        linha = ('p1', 'SKUINEXISTENTE', 2)
        uow = FakeUOW()
        messagebus.handle(comandos.CriarLote(*lote), uow)

        with raises(handlers.SkuInvalido):
            messagebus.handle(comandos.Alocar(*linha), uow)


    def test_preferir_lote_mais_antigo(self):
        sku = 'GARRAFA-VAZIA'
        lote_antigo = ('lote-antigo', sku, 20, obtem_data('ontem'))
        lote_atual = ('lote-atual', sku, 10, obtem_data('hoje'))
        lote_futuro = ('lote-futuro', sku, 30, obtem_data('amanha'))
        linha = ('pedido-001', sku, 5)

        uow = FakeUOW()

        messagebus.handle(comandos.CriarLote(*lote_antigo), uow)
        messagebus.handle(comandos.CriarLote(*lote_atual), uow)
        messagebus.handle(comandos.CriarLote(*lote_futuro), uow)
        
        [res] = messagebus.handle(comandos.Alocar(*linha), uow)

        assert res == 'lote-antigo'


class TestAlteraQuantidadeLote:
    def test_altera_quantidade_disponivel(self):
        uow = FakeUOW()

        messagebus.handle(
            comandos.CriarLote('lote1', 'SARRAFO', 100, None),
            uow
        )

        [lote] = uow.produtos.get('SARRAFO').lotes

        assert lote.quantidade_disponivel == 100

        messagebus.handle(
            comandos.AlterarQuantidadeLote('lote1', 66),
            uow
        )

        assert lote.quantidade_disponivel == 66

    def test_realocar_se_necessario(self):
        uow = FakeUOW()

        evts = [
            comandos.CriarLote('lote5', 'FONE', 55, None),
            comandos.CriarLote('lote6', 'FONE', 20, date.today()),
            comandos.Alocar('pedido5', 'FONE', 10),
            comandos.Alocar('pedido6', 'FONE', 10)
        ]

        for e in evts:
            messagebus.handle(e, uow)
        
        [lote1, lote2] = uow.produtos.get('FONE').lotes

        assert lote1.quantidade_disponivel == 35
        assert lote2.quantidade_disponivel == 20

        messagebus.handle(
            comandos.AlterarQuantidadeLote('lote5', 15),
            uow
        )

        assert lote1.quantidade_disponivel == 5
        assert lote2.quantidade_disponivel == 10
