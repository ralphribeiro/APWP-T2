from sqlalchemy.orm import mapper, relationship
from sqlalchemy.sql.schema import Column, ForeignKey, MetaData, Table
from sqlalchemy.sql.sqltypes import Integer, String, Date

from src.alocacao.dominio import modelo

metadata = MetaData()


linhas_pedido = Table(
    'linhas_pedido',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qtd', Integer, nullable=False),
    Column('pedido_id', String(255))
)

lotes = Table(
    'lotes',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('ref', String(255)),
    Column('sku', String(255)),
    Column('_qtd_comprada', Integer, nullable=False),
    Column('eta', Date, nullable=True)
)

alocacoes = Table(
    'alocacoes',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('pedido_id', ForeignKey('linhas_pedido.id')),
    Column('id_lote', ForeignKey('lotes.id')),
)


def start_mappers():
    linhas_mapeador = mapper(modelo.LinhaPedido, linhas_pedido)
    mapper(
        modelo.Lote,
        lotes,
        properties={
            '_alocacoes': relationship(
                linhas_mapeador, secondary=alocacoes, collection_class=set,
            )
        },
    )
