from __future__ import annotations
import abc

from alocacao.adapters import repository
from alocacao.camada_servicos import messagebus
from alocacao.config import DEFAULT_SESSION_FACTORY


class AbstractUOW(abc.ABC):
    produtos: repository.AbstractRepository

    def __enter__(self) -> AbstractUOW:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()
        self.publish_events()

    def publish_events(self):
        for produto in self.produtos.seen:
            while produto.eventos:
                evento = produto.eventos.pop(0)
                print(evento)
                messagebus.handle(evento)

    @abc.abstractmethod
    def _commit(self):
        pass

    @abc.abstractmethod
    def rollback(self):
        pass


class SQLAlchemyUOW(AbstractUOW):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        repo = repository.SQLAlchemyRepository(self.session)
        self.produtos = repository.TrackingRepository(repo)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
