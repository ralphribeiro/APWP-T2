from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.alocacao import config
from src.alocacao.adaptadores import orm
from src.alocacao.adaptadores.repositorio import SQLAlchemyRepositorio
from src.alocacao.dominio import modelo
from src.alocacao.camada_servicos import servicos



orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/alocar', methods=['POST'])
def alocar_endpoint():
    session = get_session()
    repo = SQLAlchemyRepositorio(session)
    linha = modelo.LinhaPedido(
        request.json['pedido_id'], request.json['sku'], request.json['qtd']
    )

    try:
        ref_lote = servicos.alocar(linha, repo, session)
    except (modelo.SemEstoque, servicos.SkuInvalido) as e:
        return {'message': str(e)}, 400

    return {'ref_lote': ref_lote}
