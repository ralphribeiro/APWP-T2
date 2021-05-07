from abc import abstractmethod


from src.alocacao.dominio import modelo


class AbstractRepository():  # porta
    @abstractmethod
    def add(self, lote: modelo.Produto):
        ...

    @abstractmethod
    def get(self, sku) -> modelo.Produto:
        ...

    @abstractmethod
    def list_all(self) -> list[modelo.Produto]:
        ...


class SQLAlchemyRepository(AbstractRepository):  # adaptador
    def __init__(self, session) -> None:
        self.session = session

    def add(self, produto: modelo.Produto):
        self.session.add(produto)

    def get(self, sku) -> modelo.Produto:
        return self.session.query(modelo.Lote).filter_by(sku=sku).one()

    def list_all(self) -> list[modelo.Produto]:
        return self.session.query(modelo.Produto).all()


class FakeRepository(AbstractRepository):  # adaptador
    def __init__(self):
        self._produtos = set()

    def add(self, produto: modelo.Produto):
        self._produtos.add(produto)

    def get(self, sku) -> modelo.Produto:
        return next(
            (produto for produto in self._produtos if produto.sku == sku),
            None
        )

    def list_all(self) -> list[modelo.Produto]:
        return list(self._produtos)
