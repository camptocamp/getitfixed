# coding=utf-8
import os
import sys
import transaction
from datetime import date, timedelta

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars


from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )

from ..models.c2cgeoform_demo import (
    schema,
    Address,
    BusStop,
    District,
    Excavation,
    Situation,
    ContactPerson
    )


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
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)

    with engine.begin() as connection:
        init_db(connection, force='--force' in options)


def init_db(connection, force=False):
    if force:
        if schema_exists(connection, schema):
            connection.execute("DROP SCHEMA {} CASCADE;".format(schema))

    if not schema_exists(connection, schema):
        connection.execute("CREATE SCHEMA \"{}\";".format(schema))

    Base.metadata.create_all(connection)

    session_factory = get_session_factory(connection)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
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
    if dbsession.query(District).count() == 0:
        dbsession.add(District(id=0, name="Pully"))
        dbsession.add(District(id=1, name="Paudex"))
        dbsession.add(District(id=2, name="Belmont-sur-Lausanne"))
        dbsession.add(District(id=3, name="Trois-Chasseurs"))
        dbsession.add(District(id=4, name="La Claie-aux-Moines"))
        dbsession.add(District(id=5, name="Savigny"))
        dbsession.add(District(id=6, name="Mollie-Margot"))

    if dbsession.query(Situation).count() == 0:
        dbsession.add(Situation(id=0, name="Road", name_fr="Route"))
        dbsession.add(Situation(id=1, name="Sidewalk", name_fr="Trottoir"))
        dbsession.add(Situation(id=2, name="Berm", name_fr="Berme"))
        dbsession.add(Situation(
            id=3, name="Vegetated berm", name_fr=u"Berme végétalisée"))
        dbsession.add(Situation(id=4, name="Green zone", name_fr="Zone verte"))
        dbsession.add(Situation(id=5, name="Cobblestone", name_fr="Pavés"))

    if dbsession.query(BusStop).count() == 0:
        _add_bus_stops(dbsession)

    if dbsession.query(Address).count() == 0:
        dbsession.add(Address(id=0, label="Bern"))
        dbsession.add(Address(id=1, label="Lausanne"))
        dbsession.add(Address(id=2, label="Genève"))
        dbsession.add(Address(id=3, label="Zurich"))
        dbsession.add(Address(id=4, label="Lugano"))

    dbsession.flush()

    if dbsession.query(Excavation).count() == 0:
        for i in range(100):
            dbsession.add(_excavation(i, dbsession))


def _excavation(i, dbsession):
    situations = dbsession.query(Situation).all()
    addresses = dbsession.query(Address).all()

    contact = ContactPerson()
    contact.first_name = 'Leonard'
    contact.last_name = 'Michalon'

    excavation = Excavation(
        reference_number='ref{:04d}'.format(i),
        request_date=date.today() - timedelta(days=100 - i),
        description="Installation d'un réseau AEP",
        motif="Création d'un lotissement",
        location_district_id=0,
        location_street="48 avenue du Lac du Bourget",
        location_postal_code="73370",
        location_town="LE BOURGET DU LAC",
        # address_id=ForeignKey('c2cgeoform_demo.address.id'),
        # location_position = Column(geoalchemy2.Geometry('POINT'
        responsible_title="mr",
        responsible_name="Morvan",
        responsible_first_name="Arnaud",
        responsible_mobile="555-55555",
        responsible_mail="arnaud.morvan@camptocamp.com",
        responsible_company="Camptocamp",
        validated=True,
        # work_footprint=geoalchemy2.Geometry('MULTIPOLYGON'
        # photos = relationship(Photo,
    )
    for j in range(0, 3):
        excavation.situations.append(situations[(i + j) % len(situations)])
    excavation.contact_persons = [contact]
    excavation.address_id = addresses[i % len(addresses)].id
    return excavation


def _add_bus_stops(dbsession):
    """
    Load test data from a GeoJSON file.
    """
    import json
    from shapely.geometry import shape

    file = open(os.path.join(os.path.dirname(__file__),
                             '..',
                             'data',
                             'osm-lausanne-bus-stops.geojson'))
    geojson = json.load(file)
    file.close()

    bus_stops = []
    for feature in geojson['features']:
        id = feature['id'].replace('node/', '')
        geometry = shape(feature['geometry'])
        name = feature['properties']['name'] \
            if 'name' in feature['properties'] else ''
        bus_stop = BusStop(
            id=int(float(id)),
            geom='SRID=4326;' + geometry.wkt,
            name=name)
        bus_stops.append(bus_stop)

    dbsession.add_all(bus_stops)
