from pyramid.events import subscriber, BeforeRender, NewRequest
from pyramid.i18n import get_localizer, TranslationStringFactory

# see https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/templates/mako_i18n.html*


@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event["request"]
    event["_"] = request.translate
    event["localizer"] = request.localizer
    event["layout"] = request.registry.settings["getitfixed"].get(
        "layout", "getitfixed:templates/layout.jinja2"
    )


tsf1 = TranslationStringFactory("getitfixed")
tsf2 = TranslationStringFactory("c2cgeoform")


@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(*args, **kwargs):
        result = localizer.translate(tsf1(*args, **kwargs))
        return (
            localizer.translate(tsf2(*args, **kwargs)) if result == args[0] else result
        )

    request.localizer = localizer
    request.translate = auto_translate
