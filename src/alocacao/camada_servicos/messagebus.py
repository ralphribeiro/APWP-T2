from logging import Logger
from typing import Callable, Union

from alocacao.dominio import comandos, eventos
from alocacao.camada_servicos import handlers, unit_of_work


logger = Logger(__name__)
Message = Union[comandos.Comando, eventos.Evento]


class MessageBus:
    def __init__(
        self,
        uow: unit_of_work.AbstractUOW,
        event_handers: dict[type[eventos.Evento], list[Callable]],
        command_handers: dict[type[comandos.Comando], Callable]
    ):
        self.uow = uow
        self.event_handers = event_handers
        self.command_handers = command_handers

    def handle(self, message: Message):
        self.queue = [message]
        results = []
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, eventos.Evento):
                self.handle_event(message)
            elif isinstance(message, comandos.Comando):
                cmd_result = self.handle_command(message)
                results.append(cmd_result)
            else:
                raise Exception(f'{message} não é um commando ou evento')

        return results

    def handle_event(
        self,
        event: eventos.Evento,
    ):
        for handler in self.event_handers[type(event)]:
            try:
                logger.debug(
                    'manipulando evento %s com o %s', event, handler
                )
                handler(event)
                self.queue.extend(self.uow.collect_new_messages())
            except Exception:
                logger.exception('Exceção ao manipular o evento %s', event)
                continue

    def handle_command(
        self,
        command: comandos.Comando,
    ):
        logger.debug('manipulando o comando %s', command)
        try:
            handler = self.command_handers[type(command)]
            result = handler(command)
            self.queue.extend(self.uow.collect_new_messages())
            return result
        except Exception:
            logger.exception('Exceção ao manipular o comando %s', command)
            raise
