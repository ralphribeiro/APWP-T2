import json
from logging import Logger
import redis

from alocacao import bootstrap, config
from alocacao.dominio import comandos
from alocacao.camada_servicos import messagebus, unit_of_work


logger = Logger(__name__)
r = redis.Redis(**config.get_redis_host_and_port())
bus = bootstrap.bootstrap()


def main():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('altera_quantidade_lote')

    for m in pubsub.listen():
        handle_altera_quantidade_lote(m)


def handle_altera_quantidade_lote(m):
    logger.debug('manipulando %s', m)
    data = json.loads(m['data'])
    cmd = comandos.AlterarQuantidadeLote(
        ref=data['ref_lote'], qtd_nova=data['qtd_nova']
    )
    bus.handle(cmd)


if __name__ == '__main__':
    main()
