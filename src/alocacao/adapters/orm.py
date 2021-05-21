from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship
from sqlalchemy.sql.schema import Column, ForeignKey, MetaData, Table
from sqlalchemy.sql.sqltypes import Integer, String, Date

from alocacao.dominio import modelo
from alocacao import views

metadata = MetaData()


linhas_pedido = Table(
    "linhas_pedido",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qtd", Integer, nullable=False),
    Column("pedido_id", String(255)),
)

lotes = Table(
    "lotes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ref", String(255)),
    Column("sku", ForeignKey("produtos.sku")),
    Column("_qtd_comprada", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

alocacoes = Table(
    "alocacoes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("pedido_id", ForeignKey("linhas_pedido.id")),
    Column("lote_id", ForeignKey("lotes.id")),
)


produtos = Table(
    "produtos",
    metadata,
    Column("sku", String(255), primary_key=True),
    Column("versao", Integer, nullable=False),
)

alocacoes_view = Table(
    "alocacoes_view",
    metadata,
    Column("pedido_id", String(255)),
    Column("sku", String(255)),
    Column("ref_lote", String(255))
)

def start_mappers():
    linhas_mapper = mapper(modelo.LinhaPedido, linhas_pedido)
    lotes_mapper = mapper(
        modelo.Lote,
        lotes,
        properties={
            "_alocacoes": relationship(
                linhas_mapper,
                secondary=alocacoes,
                collection_class=set,
            )
        },
    )
    mapper(modelo.Produto, produtos, properties={
           "lotes": relationship(lotes_mapper)})


@event.listens_for(modelo.Produto, "load")
def receive_load(produto, _):
    produto.eventos = []
