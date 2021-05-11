from typing import Protocol

from sqlalchemy.orm import Session

from alocacao.dominio import modelo


class AbstractRepository(Protocol):  # porta
    def add(self, produto: modelo.Produto) -> None: ...
    def get(self, sku) -> modelo.Produto: ...


class TrackingRepository:
    seen: set[modelo.Produto]
    def __init__(self, repo: AbstractRepository):
        self._repo = repo
        self.seen = set()

    def add(self, produto: modelo.Produto):
        self._repo.add(produto)
        self.seen.add(produto)

    def get(self, sku) -> modelo.Produto:
        produto = self._repo.get(sku)
        if produto:
            self.seen.add(produto)
        return produto


class SQLAlchemyRepository:  # adaptador
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, produto: modelo.Produto):
        self.session.add(produto)

    def get(self, sku) -> modelo.Produto:
        return self.session.query(modelo.Produto).filter_by(sku=sku).first()
