from alocacao.dominio import eventos


def handle(event: eventos.Evento):
    for handler in HANDLERS[type(event)]:
        handler(event)


def envia_notificacao_sem_estoque(event: eventos.SemEstoque):
    email.send_email(
        'estoque@apwp-t2.com',
        f'Fora de estoque for {event.sku}'
    )


HANDLERS = {eventos.SemEstoque: [envia_notificacao_sem_estoque], }
