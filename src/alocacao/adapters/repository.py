from typing import Protocol

from sqlalchemy.orm import Session

from alocacao.dominio import modelo


class AbstractRepository(Protocol): # porta
    seen: set[modelo.Produto]
    def add(self, produto: modelo.Produto) -> None: ...
    def get(self, sku) -> modelo.Produto: ...


class TrackingRepository:
    seen: set[modelo.Produto]

    def __init__(self, repo: AbstractRepository):
        self.seen = set()
        self._repo = repo

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
        self.seen: set[modelo.Produto] = set()

    def add(self, produto: modelo.Produto):
        self.session.add(produto)

    def get(self, sku) -> modelo.Produto:
        return self.session.query(modelo.Produto).filter_by(sku=sku).first()

