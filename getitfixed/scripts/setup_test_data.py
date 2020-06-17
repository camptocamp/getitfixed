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
DESCRIPTIONS = ("Déchets sur la voie publique", "Nid de poule")
FIRSTNAMES = ("Dale", "Teresa", "Beatrice", "Darcie")
LASTNAMES = ("Lamb", "Evans", "Alexander", "Rowe", "Ford")

WMS_BASE = (
    "https://geomapfish-demo-2-4.camptocamp.com/mapserv_proxy"
    "?ogcserver=Main+PNG"
    "&SERVICE=WMS"
    "&VERSION=1.3.0"
    "&REQUEST=GetMap"
    "&FORMAT=image%2Fpng"
    "&TRANSPARENT=true"
    "&SERVERTYPE=mapserver"
)
WMS_LAYERS = (
    WMS_BASE + "&LAYERS={}&STYLES=%2C".format("post_office"),
    WMS_BASE + "&LAYERS={}&STYLES=%2C".format("entertainment"),
    WMS_BASE + "&LAYERS={}&STYLES=%2C".format("sustenance"),
    None,
)


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
    from getitfixed.models import get_engine, get_session_factory, get_tm_session

    engine = get_engine(settings)
    wait_for_db(engine)

    session_factory = get_session_factory(engine)
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        setup_test_data(dbsession)


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
                    wms_layer=WMS_LAYERS[i % 4],
                )
            )
    if dbsession.query(Issue).count() == 0:
        for i in range(100):
            dbsession.add(_issue(i, (i % 15) + 1, dbsession))


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
