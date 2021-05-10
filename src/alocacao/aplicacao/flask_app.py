from datetime import date

from flask import Flask, request

from alocacao.dominio import modelo
from alocacao.camada_servicos import servicos, unit_of_work


app = Flask(__name__)


@app.route('/')
def ola():
    return 'Olá'


@app.route('/adiciona_lote', methods=['POST'])
def adiciona_lote_endpoint():
    eta = request.json['eta']
    if eta is None:
        eta = date.today()

    with unit_of_work.SQLAlchemyUOW() as uow:
        servicos.adiciona_lote(
            request.json['ref'], request.json['sku'],
            request.json['qtd'], eta, uow)

    return 'OK', 201


@app.route('/alocar', methods=['POST'])
def alocar_endpoint():
    linha = (request.json['pedido_id'],
             request.json['sku'], request.json['qtd'])
    with unit_of_work.SQLAlchemyUOW() as uow:
        try:
            ref_lote = servicos.alocar(*linha, uow)
        except (modelo.SemEstoque, servicos.SkuInvalido) as e:
            return {'message': str(e)}, 400

    return {'ref_lote': ref_lote}
