import os

from c2cgeoform.routes import register_models
from .models.c2cgeoform_demo import (
    Excavation,
)


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('node_modules', 'getitfixed:node_modules/')
    config.override_asset(to_override='getitfixed:node_modules/',
                          override_with=os.path.join(os.path.dirname(__file__),
                                                     '..',
                                                     'node_modules'))
    config.add_route('home', '/')
    config.add_route('bus_stops', '/bus_stops')
    config.add_route('addresses', '/addresses')

    register_models(config, [
        ('excavations', Excavation)])
