from typing import Protocol, Callable

from alocacao.dominio import eventos
from alocacao.camada_servicos import handlers, unit_of_work


class AbstractMessageBus(Protocol):
    HANDLERS: dict[type[eventos.Evento], type[list[Callable]]]

    def handle(event: eventos.Evento, uow: unit_of_work.AbstractUOW):
        ...
        

def handle(event: eventos.Evento, uow: unit_of_work.AbstractUOW):
    queue = [event]
    results = []
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow))
            queue.extend(uow.collect_new_events())
    return results


HANDLERS = {
    eventos.SemEstoque: [handlers.envia_notificacao_sem_estoque],
    eventos.LoteCriado: [handlers.adiciona_lote],
    eventos.AlocacaoRequerida: [handlers.alocar],
    eventos.AlteradaQuantidadeLote: [handlers.altera_qtd_lote],
}
