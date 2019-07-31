from pyramid.view import view_config

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

from ..models.c2cgeoform_demo import BusStop


@view_config(route_name='bus_stops', request_method='GET', renderer='json')
def bus_stops(request):
    stops = request.dbsession.query(BusStop).all()
    return {
        'type': 'FeatureCollection',
        'features': [{
                'type': 'Feature',
                'id': stop.id,
                'properties': {
                    'name': stop.name},
                'geometry': mapping(to_shape(stop.geom))
        } for stop in stops]
    }
