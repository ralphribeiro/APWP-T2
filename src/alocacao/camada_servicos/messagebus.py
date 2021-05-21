from logging import Logger
from typing import Union

from tenacity import (
    Retrying, RetryError, stop_after_attempt, wait_random_exponential
)

from alocacao.dominio import comandos, eventos
from alocacao.camada_servicos import handlers, unit_of_work


logger = Logger(__name__)
Message = Union[comandos.Comando, eventos.Evento]


def handle(message: Message, uow: unit_of_work.AbstractUOW):
    queue = [message]
    results = []
    while queue:
        message = queue.pop(0)
        if isinstance(message, eventos.Evento):
            handle_event(message, queue, uow)
        elif isinstance(message, comandos.Comando):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f'{message} não é um commando ou evento')

    return results


def handle_event(
    event: eventos.Evento,
    queue: list[Message],
    uow: unit_of_work.AbstractUOW
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug(
                'manipulando evento %s com o %s', event, handler
            )
            handler(event, uow)
            queue.extend(uow.collect_new_messages())
        except Exception:
            logger.exception('Exceção ao manipular o evento %s', event)
            continue


def handle_command(
    command: comandos.Comando,
    queue: list[Message],
    uow: unit_of_work.AbstractUOW
):
    logger.debug('manipulando o comando %s', command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow)
        queue.extend(uow.collect_new_messages())
        return result
    except Exception:
        logger.exception('Exceção ao manipular o comando %s', command)
        raise


EVENT_HANDLERS = {
    eventos.SemEstoque: [handlers.envia_notificacao_sem_estoque],
    eventos.Alocado: [
        handlers.publica_evento_alocado,
        handlers.adiciona_alocacao_ao_modelo_de_leitura
    ],
    eventos.Desalocado: [
        handlers.remove_alocacao_do_modelo_de_leitura,
        handlers.realocar
    ],
}

COMMAND_HANDLERS = {
    comandos.CriarLote: handlers.adiciona_lote,
    comandos.Alocar: handlers.alocar,
    comandos.AlterarQuantidadeLote: handlers.altera_qtd_lote
}
