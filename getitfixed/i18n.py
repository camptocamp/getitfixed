from pyramid.i18n import default_locale_negotiator
from pyramid.settings import aslist
from translationstring import TranslationStringFactory


_ = TranslationStringFactory('getitfixed')


def locale_negotiator(request):
    locale_name = default_locale_negotiator(request)

    # available languages are not handled by pyramid itself
    if locale_name is None:
        available = aslist(request.registry.settings['pyramid.available_languages'])
        locale_name = request.accept_language.best_match(available)

    return locale_name
