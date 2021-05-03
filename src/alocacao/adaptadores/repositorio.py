from abc import abstractmethod


from src.alocacao.dominio import modelo


class RepositorioAbstrato():
    @abstractmethod
    def insere(self, lote: modelo.Lote):
        ...

    @abstractmethod
    def obtem(self, referencia) -> modelo.Lote:
        ...


class SQLAlchemyRepositorio(RepositorioAbstrato):
    def __init__(self, session) -> None:
        self.session = session

    def add(self, lote: modelo.Lote):
        self.session.add(lote)

    def get(self, ref) -> modelo.Lote:
        return self.session.query(modelo.Lote).filter_by(ref=ref).one()

    def list_all(self):
        return self.session.query(modelo.Lote).all()
