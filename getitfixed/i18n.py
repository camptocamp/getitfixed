from pyramid.i18n import default_locale_negotiator
from pyramid.settings import aslist
from translationstring import TranslationStringFactory


_ = TranslationStringFactory("getitfixed")


def locale_negotiator(request):
    locale_name = default_locale_negotiator(request)

    # available languages are not handled by pyramid itself
    if locale_name is None:
        available = aslist(request.registry.settings["pyramid.available_languages"])
        default = request.registry.settings["pyramid.default_locale_name"]
        locale_name = request.accept_language.lookup(available, default=default)

    return locale_name
