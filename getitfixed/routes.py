import os

from c2cgeoform.routes import pregenerator
from getitfixed.models.getitfixed import Event, Issue


def includeme(config):
    config.add_static_view("getitfixed_static", "getitfixed:static", cache_max_age=3600)
    config.add_static_view("getitfixed_node_modules", "getitfixed:node_modules/")
    config.override_asset(
        to_override="getitfixed:node_modules/",
        override_with=os.path.join(os.path.dirname(__file__), "..", "node_modules"),
    )
    config.add_route("getitfixed", "/getitfixed")

    config.add_c2cgeoform_application("getitfixed", [("issues", Issue)])
    config.add_c2cgeoform_application("admin", [("issues", Issue), ("event", Event)])
    config.add_route(
        "c2cgeoform_item_private",
        "{application:admin|getitfixed}/private/{table}/{id}",
        pregenerator=pregenerator,
    )
    config.add_route("issues_geojson", "{application}/{table}/data/geojson.json")
