from pyramid.config import Configurator
from pkg_resources import resource_filename

from c2c.template.config import config as configuration
import c2cgeoform

search_paths = (
    resource_filename("getitfixed", "templates/widgets"),
) + c2cgeoform.default_search_paths
c2cgeoform.default_search_paths = search_paths


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(
        settings=settings, locale_negotiator="getitfixed.i18n.locale_negotiator"
    )

    # Update the settings object from the YAML application config file
    configuration.init(settings.get("app.cfg"))
    config.get_settings().update(configuration.get_config())

    # config.include('c2cwsgiutils.pyramid.includeme')
    config.include("pyramid_jinja2")
    config.include("c2cgeoform")
    config.include(".models")
    config.include(".routes")
    c2cgeoform.routes.register_routes(config)

    config.add_translation_dirs("locale")

    config.scan()

    return config.make_wsgi_app()
