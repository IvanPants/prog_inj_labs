import time

import loguru
import pytest
from loguru import logger
from pymongo import MongoClient

from src.config import get_config, logger_set_up


# client = MongoClient()
# client = MongoClient(host="localhost", port=27017)
# print(client)

def test_always_ok(settings, logger_ready):
    logger.info(f'Test always ok is ok (lol)!')
    time.sleep(0.1)
    pass


def test_fixture_client(settings, logger_ready, client):
    logger.debug(f'Test fixture client!')
    logger.debug(f'Client: {client}')
    time.sleep(0.1)


def test_mongo_client_manual(settings, logger_ready):
    logger = loguru.logger.bind(object_id='MONGO_TEST')
    logger.trace("Test mongo connection")
    logger.trace("Test mongo client manual")
    # uri = "mongodb://127.0.0.1"

    delay = 3000  # milliseconds=
    try:
        logger.debug(f'Using url: {settings.db_host}:{settings.db_port}, delay: {delay}')
        client = MongoClient(host=settings.db_host, port=settings.db_port, serverSelectionTimeoutMS=delay)
        # client = MongoClient(uri, serverSelectionTimeoutMS=delay)

        client.admin.command("ping")
        logger.info("Connected successfully")
        logger.debug(f'Closing client...')
        client.close()
    except Exception as e:
        logger.error(f'Error: {repr(e)}')

    time.sleep(0.2)


def test_mongo_connection(settings, logger_ready, client):
    logger = loguru.logger.bind(object_id='MONGO_TEST')
    logger.trace("Test mongo connection")
    try:
        client.admin.command("ping")
        logger.info("Connected successfully")
    except Exception as e:
        logger.error(f'Error: {repr(e)}')

    time.sleep(0.2)


# region Fixtures
@pytest.fixture(scope='module')
def client(settings):
    client = MongoClient(host=settings.db_host, port=settings.db_port)
    yield client
    client.close()


@pytest.fixture(scope='module')
def settings():
    # print(f'Fixture working!')
    app_settings = get_config()
    yield app_settings
    # print(f'Fixture ended!')


@pytest.fixture(scope='module')
def logger_ready(settings):
    logger_set_up(settings)

# endregion Fixtures
