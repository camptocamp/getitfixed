from pkg_resources import resource_filename
from pyramid.config import Configurator

from c2c.template.config import config as configuration
import c2cgeoform

search_paths = (
    resource_filename("getitfixed", "templates/widgets"),
) + c2cgeoform.default_search_paths
c2cgeoform.default_search_paths = search_paths


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Update the settings object from the YAML application config file
    configuration.init(settings.get("app.cfg"))
    settings.update(configuration.get_config())

    config = Configurator(
        settings=settings, locale_negotiator="getitfixed.i18n.locale_negotiator"
    )

    config.include("getitfixed")
    config.include("getitfixed.models")
    c2cgeoform.routes.register_routes(config)

    def notfound_view(request):
        request.response.status = 404
        return {}

    config.add_notfound_view(
        notfound_view, append_slash=True, renderer="getitfixed:templates/404.jinja2"
    )

    return config.make_wsgi_app()


def includeme(config: Configurator):
    config.include("pyramid_jinja2")
    config.include("c2cgeoform")
    config.include(".routes")
    config.add_translation_dirs("getitfixed:locale")
    config.scan()
