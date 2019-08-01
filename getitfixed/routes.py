import os

from c2cgeoform.routes import register_application
from getitfixed.models.getitfixed import (
    Issue,
)


def includeme(config):
    config.add_static_view('getitfixed_static', 'getitfixed:static', cache_max_age=3600)
    config.add_static_view('node_modules', 'getitfixed:node_modules/')
    config.override_asset(to_override='getitfixed:node_modules/',
                          override_with=os.path.join(os.path.dirname(__file__),
                                                     '..',
                                                     'node_modules'))
    config.add_route('getitfixed', '/getitfixed')
    config.add_route('bus_stops', '/bus_stops')
    config.add_route('addresses', '/addresses')

    register_application(
        'getitfixed',
        [
            ('issues', Issue)
        ]
    )
