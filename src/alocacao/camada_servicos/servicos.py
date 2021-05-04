from src.alocacao.dominio import modelo
from src.alocacao.dominio.modelo import LinhaPedido
from src.alocacao.adaptadores.repositorio import RepositorioAbstrato


class SkuInvalido(Exception):
    ...


def sku_valido(sku, lotes) -> bool:
    return sku in {lote.sku for lote in lotes}


def alocar(linha: LinhaPedido, repo: RepositorioAbstrato, session) -> str:
    lotes = repo.list_all()
    if not sku_valido(linha.sku, lotes):
        raise SkuInvalido(f'Sku inválido {linha.sku}')
    ref = modelo.alocar(linha, lotes)
    session.commit()
    return ref
