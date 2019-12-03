from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


@view_config(route_name="getitfixed_admin", permission="getitfixed_admin")
def getitfixed(request):
    return HTTPFound(
        request.route_url(
            "c2cgeoform_index", application="getitfixed_admin", table="issues"
        )
    )
