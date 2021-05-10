from abc import abstractmethod

from sqlalchemy.orm import Session

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
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, produto: modelo.Produto):
        self.session.add(produto)

    def get(self, sku) -> modelo.Produto:
        # import pdb; pdb.set_trace()
        ret = self.session.query(modelo.Produto).filter_by(sku=sku).one()
        return ret

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
