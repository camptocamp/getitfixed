from c2cgeoform.routes import pregenerator
from getitfixed.models.getitfixed import Event, Issue


def includeme(config):
    getitfixed_settings = config.get_settings()["getitfixed"]

    routes = {
        **{
            "getitfixed": "getitfixed",
            "getitfixed_private": "getitfixed_private",
            "getitfixed_admin": "getitfixed_admin",
        }
        **getitfixed_settings.get("routes", {}),
    }

    config.add_static_view("getitfixed_static", "getitfixed:static", cache_max_age=3600)

    config.add_route("getitfixed", "/getitfixed/")
    config.add_c2cgeoform_application(
        "getitfixed",
        [("issues", Issue)],
        segment_url="signalez-nous",
    )

    config.add_c2cgeoform_application(
        "getitfixed_private",
        [],
        segment_url=routes["getitfixed_private"],
    )

    # Temporary redirect URLs sent by email to new URL
    config.add_route(
        "c2cgeoform_item_private",
        "{application:getitfixed}/private/{table}/{id}",
        pregenerator=pregenerator,
    )

    config.add_route("getitfixed_admin", "/{}_admin/".format())
    config.add_c2cgeoform_application(
        "getitfixed_admin",
        [("issues", Issue), ("event", Event)],
        segment_url=routes["getitfixed_admin"],
    )
    config.add_route(
        "getitfixed_set_private",
        "/{application:getitfixed_admin}/{table:issues}/{id}/set_private",
        pregenerator=pregenerator,
    )
    config.add_route(
        "getitfixed_set_public",
        "/{application:getitfixed_admin}/{table:issues}/{id}/set_public",
        pregenerator=pregenerator,
    )
