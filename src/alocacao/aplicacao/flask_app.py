from datetime import date

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.alocacao import config
from src.alocacao.adapters import orm
from src.alocacao.adapters.repository import SQLAlchemyRepository
from src.alocacao.dominio import modelo
from src.alocacao.camada_servicos import servicos


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/adiciona_lote', methods=['POST'])
def adiciona_lote_endpoint():
    session = get_session()
    repo = SQLAlchemyRepository(session)

    eta = request.json['eta']
    if eta is None:
        eta = date.today()

    servicos.adiciona_lote(
        request.json['ref'], request.json['sku'],
        request.json['qtd'], eta, repo, session)

    return 'OK', 201
    


@app.route('/alocar', methods=['POST'])
def alocar_endpoint():
    session = get_session()
    repo = SQLAlchemyRepository(session)
    linha = (request.json['pedido_id'],
             request.json['sku'], request.json['qtd'])

    try:
        ref_lote = servicos.alocar(*linha, repo, session)
    except (modelo.SemEstoque, servicos.SkuInvalido) as e:
        return {'message': str(e)}, 400

    return {'ref_lote': ref_lote}
