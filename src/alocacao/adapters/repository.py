from abc import abstractmethod


from src.alocacao.dominio import modelo


class AbstractRepository():  # porta
    @abstractmethod
    def add(self, lote: modelo.Lote):
        ...

    @abstractmethod
    def get(self, ref) -> modelo.Lote:
        ...

    @abstractmethod
    def list_all(self) -> list[modelo.Lote]:
        ...


class SQLAlchemyRepository(AbstractRepository):  # adaptador
    def __init__(self, session) -> None:
        self.session = session

    def add(self, lote: modelo.Lote):
        self.session.add(lote)

    def get(self, ref) -> modelo.Lote:
        return self.session.query(modelo.Lote).filter_by(ref=ref).one()

    def list_all(self) -> list[modelo.Lote]:
        return self.session.query(modelo.Lote).all()


class FakeRepository(AbstractRepository):  # adaptador
    def __init__(self):
        self._lotes = set()

    def add(self, lote: modelo.Lote):
        self._lotes.add(lote)

    def get(self, ref) -> modelo.Lote:
        return next(lote for lote in self._lotes if lote.ref == ref)

    def list_all(self) -> list[modelo.Lote]:
        return list(self._lotes)
