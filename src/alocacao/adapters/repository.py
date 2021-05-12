from typing import Protocol

from sqlalchemy.orm import Session

from alocacao.dominio import modelo
from alocacao.adapters import orm


class AbstractRepository(Protocol):  # porta
    def add(self, produto: modelo.Produto) -> None:
        ...

    def get(self, sku) -> modelo.Produto:
        ...

    def get_by_ref(self, lote_ref) -> modelo.Produto:
        ...


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

    def get_by_ref(self, lote_ref) -> modelo.Produto:
        produto = self._repo.get_by_ref(lote_ref)
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

    def get_by_ref(self, lote_ref) -> modelo.Produto:
        return (
            self.session.query(modelo.Produto)
            .join(modelo.Lote)
            .filter(orm.lotes.c.ref == lote_ref)
            .first()
        )
