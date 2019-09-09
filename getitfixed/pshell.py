from contextlib import suppress
from transaction.interfaces import NoTransaction

# from webtest import TestApp


def setup(env):
    request = env["request"]

    # env['testapp'] = TestApp(env['app'])

    # start a transaction which can be used in the shell
    request.tm.begin()

    # if using the SQLAlchemy backend from our cookiecutter, the dbsession is
    # connected to the transaction manager above
    env["tm"] = request.tm
    env["s"] = request.dbsession
    try:
        yield

    finally:
        with suppress(NoTransaction):
            request.tm.abort()
