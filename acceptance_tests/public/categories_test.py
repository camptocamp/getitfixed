import pytest
import webtest

from getitfixed.models.getitfixed import Category, Type
from getitfixed.scripts.setup_test_data import WMS_LAYERS

from ..model_test import ICONS


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("dbsession", "transact")
def categories_test_data(dbsession, transact):
    del transact

    categories = []
    for i in range(5):
        categories.append(
            Category(
                label_en="Category «{}»".format(i),
                label_fr="Catégorie «{}»".format(i),
                email="{}.is@abit.ch".format(i),
                icon=ICONS[i][0],
            )
        )
    dbsession.add_all(categories)

    types = []
    for i in range(15):
        types.append(
            Type(
                label_en="Type «{}»".format(i),
                label_fr="Type «{}»".format(i),
                category=categories[i % 3],
                wms_layer=WMS_LAYERS[i % 4],
            )
        )
    dbsession.add_all(types)

    yield {"categories": categories, "types": types}


@pytest.mark.usefixtures("categories_test_data", "test_app")
class TestCategories():

    @pytest.mark.parametrize("locale", ["en", "fr"])
    def test_success(self, test_app, categories_test_data, locale):
        categories = categories_test_data["categories"]

        test_app.set_cookie("_LOCALE_", locale)
        result = test_app.get("/getitfixed/categories.json", status=200).json

        assert len(result) == len(categories)
        for c, exp_c, icon in zip(result, categories, ICONS):
            assert c["id"] == exp_c.id
            assert c["label"] == exp_c.label(locale)
            assert c["icon"] == icon[-1]
            for t, exp_t in zip(c["types"], exp_c.types):
                assert t["id"] == exp_t.id
                assert t["label"] == exp_t.label(locale)
                assert t["wms_layer"] == exp_t.wms_layer
