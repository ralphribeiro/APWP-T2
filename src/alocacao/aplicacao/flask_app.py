from datetime import date

from flask import Flask, jsonify, request

from alocacao import views
from alocacao.adapters import orm
from alocacao.dominio import comandos
from alocacao.camada_servicos import handlers, messagebus, unit_of_work


app = Flask(__name__)
orm.start_mappers()


@app.route("/")
def ola():
    return "Olá", 200


@app.route("/adiciona_lote", methods=["POST"])
def adiciona_lote_endpoint():
    eta = request.json["eta"]
    if eta is None:
        eta = date.today()

    uow = unit_of_work.SQLAlchemyUOW()

    messagebus.handle(
        comandos.CriarLote(
            request.json["ref"], request.json["sku"], request.json["qtd"], eta
        ), uow
    )

    return "OK", 201


@app.route("/alocar", methods=["POST"])
def alocar_endpoint():
    linha = (
        request.json["pedido_id"], request.json["sku"], request.json["qtd"]
    )
    with unit_of_work.SQLAlchemyUOW() as uow:
        try:
            comando = comandos.Alocar(*linha)
            resultados = messagebus.handle(comando, uow)
            ref_lote = resultados.pop(0)
        except handlers.SkuInvalido as e:
            return {"message": str(e)}, 400

    return {"ref_lote": ref_lote}, 201


@app.route("/alocacao/<pedido_id>", methods=["GET"])
def  obtem_alocacao(pedido_id):
    with unit_of_work.SQLAlchemyUOW() as uow:
        result = views.alocacoes(pedido_id, uow)
        if not result:
            return 'not found', 404
        return jsonify(result), 200
