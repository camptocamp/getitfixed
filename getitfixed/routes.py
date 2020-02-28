from c2cgeoform.routes import pregenerator
from getitfixed.models.getitfixed import Event, Issue


def includeme(config):
    config.add_static_view("getitfixed_static", "getitfixed:static", cache_max_age=3600)

    config.add_route("getitfixed", "/getitfixed/")
    config.add_c2cgeoform_application("getitfixed", [("issues", Issue)])

    config.add_route(
        "c2cgeoform_item_private",
        "{application:getitfixed}/private/{table}/{id}",
        pregenerator=pregenerator,
    )

    config.add_route("getitfixed_admin", "/getitfixed_admin")
    config.add_c2cgeoform_application(
        "getitfixed_admin", [("issues", Issue), ("event", Event)]
    )
