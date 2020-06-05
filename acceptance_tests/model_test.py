import pytest

from getitfixed.models.getitfixed import Category, Type, Issue, STATUS_IN_PROGRESS


ICONS = [
    ("https://server.com/static/image.png",),
    ("/static/image.png",),
    ("static/image.png",),
    ("static://getitfixed:static/image.png", "http://localhost/getitfixed_static/image.png"),
    (None, "http://localhost/getitfixed_static/icons/cat-default.png"),
]


def category(**kwargs):
    defaults = {
        "label_en": "Category",
        "label_fr": "Catégorie",
        "email": "is@abit.ch",
    }
    return Category(**{**defaults, **kwargs})


def type_(**kwargs):
    defaults = {
        "label_en": "Type (en)",
        "label_fr": "Type (fr)",
    }
    return Type(
        category=category(**kwargs.pop("category", {})),
        **{**defaults,**kwargs},
    )


def issue(**kwargs):
    defaults = {
        "description": "description",
        "localisation": "localisation",
        "firstname": "firstname",
        "lastname": "lastname",
        "phone": "0479000000",
        "status": STATUS_IN_PROGRESS,
        "email": "firstname.lastname@domain.net",
    }
    return Issue(
        type=type_(**kwargs.pop("type", {})),
        **{**defaults, **kwargs},
    )


class TestCategory():
    def test_label(self):
        c = category()
        assert c.label("en") == "Category"
        assert c.label("fr") == "Catégorie"

    @pytest.mark.parametrize("icon,icon_url", [(i[0], i[-1]) for i in ICONS])
    @pytest.mark.usefixtures("app_env")
    def test_icon_url(self, app_env, icon, icon_url):
        request = app_env["request"]
        assert category(icon=icon).icon_url(request) == icon_url


class TestType():
    def test_label(self):
        t = type_()
        assert t.label("en") == "Type (en)"
        assert t.label("fr") == "Type (fr)"


class TestIssue:
    def test_status_i18n(self):
        i = issue()
        assert i.status_de == "In progress"  # FIXME: after de translations are done
        assert i.status_en == "In progress"
        assert i.status_fr == "En cours"

    @pytest.mark.parametrize("icon,icon_url", [(i[0], i[-1]) for i in ICONS])
    @pytest.mark.usefixtures("app_env")
    def test_icon_url(self, app_env, icon, icon_url):
        request = app_env["request"]
        i = issue(
            type={
                "category": {"icon": icon}
            }
        )
        assert i.category.icon == icon
        assert i.icon_url(request) == icon_url
