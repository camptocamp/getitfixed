import pytest
import transaction
import threading
from alembic.config import Config
from alembic import command
from pyramid import testing
from pyramid.paster import bootstrap
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from webtest import TestApp
from wsgiref.simple_server import make_server

from getitfixed.models import get_engine, get_session_factory, get_tm_session
from getitfixed.scripts import wait_for_db


@pytest.fixture(scope="session")
def app_env():
    with bootstrap("tests.ini") as env:
        yield env


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("settings")
def dbsession(settings):
    alembic_cfg = Config("alembic.ini", ini_section="getitfixed")
    command.upgrade(alembic_cfg, "head")

    engine = get_engine(settings)
    wait_for_db(engine)
    session_factory = get_session_factory(engine)
    session = get_tm_session(session_factory, transaction.manager)
    return session


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("app_env")
def settings(app_env):
    yield app_env.get("registry").settings


@pytest.fixture()  # noqa: F811
@pytest.mark.usefixtures("dbsession", "app_env")
def test_app(request, dbsession, settings, app_env):
    config = testing.setUp(registry=app_env["registry"])
    config.add_request_method(lambda request: dbsession, "dbsession", reify=True)
    """
    config.add_route('user_add', 'user_add')
    config.add_route('users_nb', 'users_nb')
    config.scan(package='acceptance_tests')
    """
    app = config.make_wsgi_app()
    testapp = TestApp(app)
    yield testapp


@pytest.fixture(scope="session")  # noqa: F811
@pytest.mark.usefixtures("dbsession", "app_env")
def selenium_app(request, dbsession, settings, app_env):
    app = app_env.get("app")
    srv = make_server("", 6543, app)
    threading.Thread(target=srv.serve_forever).start()
    yield ()
    srv.shutdown()


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("dbsession")
def transact(dbsession):
    t = dbsession.begin_nested()
    yield
    t.rollback()


def raise_db_error(Table):
    raise DBAPIError("this is a test !", None, None)


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("dbsession")
def raise_db_error_on_query(dbsession):
    query = dbsession.query
    dbsession.query = raise_db_error
    yield
    dbsession.query = query
