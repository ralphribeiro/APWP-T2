import time

from pathlib import Path
import pytest
import requests
from requests.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from src.alocacao import config
from src.alocacao.adaptadores.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail('Postgres never came up')


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail('API never came up')


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def add_lote(postgres_session):
    lotes_adicionados = set()
    skus_adicionados = set()

    def _add_lote(linhas):
        for ref, sku, qtd, eta in linhas:
            postgres_session.execute(
                'INSERT INTO lotes (ref, sku, _qtd_comprada, eta) '
                'VALUES (:ref, :sku, :qtd, :eta)',
                dict(ref=ref, sku=sku, qtd=qtd, eta=eta)
            )
            [[lote_id]] = postgres_session.execute(
                'SELECT id FROM lotes WHERE ref=:ref AND sku=:sku',
                dict(ref=ref, sku=sku)
            )
            lotes_adicionados.add(lote_id)
            skus_adicionados.add(sku)
        postgres_session.commit()

    yield _add_lote

    for lote_id in lotes_adicionados:
        postgres_session.execute(
            'DELETE FROM alocacoes WHERE lote_id=:lote_id',
            dict(lote_id=lote_id)
        )
        postgres_session.execute(
            'DELETE FROM lotes WHERE id=:lote_id',
            dict(lote_id=lote_id)
        )
    for sku in skus_adicionados:
        postgres_session.execute(
            'DELETE FROM linhas_pedido WHERE sku=:sku',
            dict(sku=sku)
        )
    postgres_session.commit()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / 'flask_app.py').touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
