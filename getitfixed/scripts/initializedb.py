# coding=utf-8
import os
import sys
import transaction
import random
from datetime import date, timedelta
from random import randrange

from pyramid.scripts.common import parse_vars, get_config_loader

from getitfixed.scripts import wait_for_db

ICONS = ["gif-black.png", "gif-green.png", "gif-red.png"]


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(
        "usage: %s <config_uri> [var=value]\n"
        '(example: "%s development.ini")' % (cmd, cmd)
    )
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])

    loader = get_config_loader(config_uri)
    loader.setup_logging()
    settings = loader.get_wsgi_app_settings(defaults=options)

    # Import the model after settings are loaded
    from getitfixed.models import get_engine

    engine = get_engine(settings)
    wait_for_db(engine)

    with engine.begin() as connection:
        init_db(
            connection, force="--force" in options, with_data="--with-data" in options
        )


def init_db(connection, force=False, with_data=False):
    # Import the model after settings are loaded
    from getitfixed.models import get_session_factory, get_tm_session
    from getitfixed.models.getitfixed import schema
    from getitfixed.models.meta import Base

    if force:
        if schema_exists(connection, schema):
            connection.execute("DROP SCHEMA {} CASCADE;".format(schema))

    if not schema_exists(connection, schema):
        connection.execute('CREATE SCHEMA "{}";'.format(schema))

    Base.metadata.create_all(connection)

    session_factory = get_session_factory(connection)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        if with_data:
            setup_test_data(dbsession)


def schema_exists(connection, schema_name):
    sql = """
SELECT count(*) AS count
FROM information_schema.schemata
WHERE schema_name = '{}';
""".format(
        schema_name
    )
    result = connection.execute(sql)
    row = result.first()
    return row[0] == 1


def get_geometry(dbsession):
    coord_x = random.uniform(5.9559113, 10.4922941)
    coord_y = random.uniform(45.817995, 47.8084648)
    result_proxy = dbsession.execute(
        "SELECT ST_SetSRID( ST_Point( {}, {}), 4326) as geom;".format(coord_x, coord_y)
    )
    return result_proxy.first()[0]


def setup_test_data(dbsession):
    # Import the model after settings are loaded
    from getitfixed.models.getitfixed import Issue, Category, Type

    if dbsession.query(Category).count() == 0:
        for i in range(4):
            dbsession.add(
                Category(
                    label_en="Category «{}»".format(i),
                    label_fr="Catégorie «{}»".format(i),
                    email="test{}@toto.com".format(i),
                    icon="static://getitfixed:static/icons/{}".format(ICONS[i % 3])
                    if i != 3
                    else None,
                )
            )
    if dbsession.query(Type).count() == 0:
        for i in range(15):
            dbsession.add(
                Type(
                    label_en="Type «{}»".format(i),
                    label_fr="Type «{}»".format(i),
                    category_id=(i % 4) + 1,
                )
            )
    if dbsession.query(Issue).count() == 0:
        for i in range(100):
            dbsession.add(_issue(i, (i % 15) + 1, dbsession))


DESCRIPTIONS = ("Déchets sur la voie publique", "Nid de poule")

FIRSTNAMES = ("Dale", "Teresa", "Beatrice", "Darcie")

LASTNAMES = ("Lamb", "Evans", "Alexander", "Rowe", "Ford")


def get_value(col, i):
    return col[i % len(col)]


def _issue(i, type_id, dbsession):
    from getitfixed.models.getitfixed import Issue, STATUSES

    STATUSES = list(STATUSES.keys())

    issue = Issue(
        request_date=date.today() - timedelta(days=100 - i),
        type_id=type_id,
        description=get_value(DESCRIPTIONS, i),
        localisation="{} rue du pont".format(i),
        geometry=get_geometry(dbsession),
        # position
        # photos
        firstname=get_value(FIRSTNAMES, i),
        lastname=get_value(LASTNAMES, i),
        phone="0{} {:02} {:02} {:02} {:02}".format(
            randrange(1, 10), *[randrange(100) for i in range(4)]
        ),
        status=STATUSES[i % 5],
    )
    issue.email = "{}.{}@domain.net".format(
        issue.firstname.lower(), issue.lastname.lower()
    )
    return issue
