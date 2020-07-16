from pyramid.view import view_config

from getitfixed.models.getitfixed import Category


@view_config(
    route_name="c2cgeoform_index",
    match_param=("application=getitfixed", "table=categories.json"),
    request_method="GET",
    renderer="json",
)
def categories(request):
    return [
        {
            "id": c.id,
            "label": c.label(request.locale_name),
            "icon": c.icon_url(request),
            "types": [
                {
                    "id": t.id,
                    "label": t.label(request.locale_name),
                    "wms_layer": t.wms_layer,
                }
                for t in c.types
            ],
        }
        for c in request.dbsession.query(Category)
    ]
