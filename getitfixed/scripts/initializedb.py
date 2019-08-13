# coding=utf-8
import os
import sys
import transaction
from datetime import date, timedelta

from pyramid.scripts.common import parse_vars, get_config_loader

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )

from getitfixed.models.getitfixed import (
    schema,
    Issue,
    )

from getitfixed.scripts import wait_for_db


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])

    loader = get_config_loader(config_uri)
    loader.setup_logging()
    settings = loader.get_wsgi_app_settings(defaults=options)

    engine = get_engine(settings)
    wait_for_db(engine)

    with engine.begin() as connection:
        init_db(connection, force='--force' in options, with_data='--with-data' in options)


def init_db(connection, force=False, with_data=False):
    if force:
        if schema_exists(connection, schema):
            connection.execute("DROP SCHEMA {} CASCADE;".format(schema))

    if not schema_exists(connection, schema):
        connection.execute("CREATE SCHEMA \"{}\";".format(schema))

    Base.metadata.create_all(connection)

    session_factory = get_session_factory(connection)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        if with_data:
            setup_test_data(dbsession)


def schema_exists(connection, schema_name):
    sql = '''
SELECT count(*) AS count
FROM information_schema.schemata
WHERE schema_name = '{}';
'''.format(schema_name)
    result = connection.execute(sql)
    row = result.first()
    return row[0] == 1


def setup_test_data(dbsession):
    if dbsession.query(Issue).count() == 0:
        for i in range(100):
            dbsession.add(_issue(i, dbsession))


DESCRIPTIONS = (
    'Déchets sur la voie publique',
    'Nit de poule',
)


def _issue(i, dbsession):
    issue = Issue(
        request_date=date.today() - timedelta(days=100 - i),
        description=DESCRIPTIONS[i % len(DESCRIPTIONS)],
        # location_position = Column(geoalchemy2.Geometry('POINT'
        # photos = relationship(Photo,
    )
    return issue
