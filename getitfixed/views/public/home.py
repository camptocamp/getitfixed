from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


@view_config(route_name="getitfixed")
def getitfixed(request):
    return HTTPFound(
        request.route_url("c2cgeoform_index", application="getitfixed", table="issues")
    )
