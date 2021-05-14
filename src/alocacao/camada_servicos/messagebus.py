from alocacao.dominio import eventos
from alocacao.camada_servicos import unit_of_work, handlers


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
