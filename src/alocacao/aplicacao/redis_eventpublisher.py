import json
from dataclasses import asdict
from logging import Logger
import redis


from alocacao import config
from alocacao.dominio import eventos


logger = Logger(__name__)
r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel, event: eventos.Evento):
    logger.debug('publicando=%s, evento=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))
