import inspect
from typing import Callable


from alocacao.adapters import orm
from alocacao.adapters.notifications import AbstractNotifications
from alocacao.aplicacao import redis_eventpublisher
from alocacao.camada_servicos import unit_of_work, messagebus, handlers


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUOW = unit_of_work.SQLAlchemyUOW(),
    notifications: AbstractNotifications = None,
    publish: Callable = redis_eventpublisher.publish
) -> messagebus.MessageBus:

    if start_orm:
        orm.start_mappers()

    dependencies = {'uow': uow,
                    'notifications': notifications, 'publish': publish}

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies)
            for handler in event_handlers
        ]
        for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }

    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handers=injected_event_handlers,  # type: ignore
        command_handers=injected_command_handlers  # type: ignore
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
