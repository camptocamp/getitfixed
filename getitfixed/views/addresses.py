from pyramid.view import view_config

from pyramid.httpexceptions import HTTPBadRequest
from ..models.c2cgeoform_demo import Address


@view_config(route_name='addresses', request_method='GET', renderer='json')
def addresses(request):
    if 'term' not in request.params:
        return HTTPBadRequest()
    term = '%%%s%%' % request.params['term']
    query = request.dbsession.query(Address).filter(Address.label.ilike(term))
    return [{'id': addr.id, 'label': addr.label} for addr in query]
