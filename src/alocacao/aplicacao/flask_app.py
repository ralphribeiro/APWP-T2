from datetime import date

from flask import Flask, jsonify, request

from alocacao import bootstrap, views
from alocacao.dominio import comandos
from alocacao.camada_servicos import handlers


app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/")
def ola():
    return "Olá", 200


@app.route("/adiciona_lote", methods=["POST"])
def adiciona_lote_endpoint():
    eta = request.json["eta"]
    if eta is None:
        eta = date.today()
    bus.handle(comandos.CriarLote(
        request.json["ref"], request.json["sku"], request.json["qtd"], eta
    ))

    return "OK", 201


@app.route("/alocar", methods=["POST"])
def alocar_endpoint():
    linha = (
        request.json["pedido_id"], request.json["sku"], request.json["qtd"]
    )
    try:
        comando = comandos.Alocar(*linha)
        resultados = bus.handle(comando)
        ref_lote = resultados.pop(0)
    except handlers.SkuInvalido as e:
        return {"message": str(e)}, 400

    return {"ref_lote": ref_lote}, 201


@app.route("/alocacao/<pedido_id>", methods=["GET"])
def obtem_alocacao(pedido_id):
    result = views.alocacoes(pedido_id, bus.uow)
    if not result:
        return 'not found', 404
    return jsonify(result), 200
