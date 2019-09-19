import pytest


@pytest.mark.usefixtures("test_app")
class TestI18n:
    def test_index(self, test_app):
        resp = test_app.get("/getitfixed/issues", status=200)

        resp_tmp = resp.click(verbose=True, href="language=en")
        resp_en = resp_tmp.follow()
        html_en = resp_en.html
        news_en = html_en.select('a[href$="/getitfixed/issues/new"]')
        assert 1 == len(news_en)
        assert ["Report an issue"] == list(news_en[0].stripped_strings)

        reference_numbers = html_en.select("th[data-field=id]")
        assert 0 == len(reference_numbers)

        resp_tmp = resp_en.click(verbose=True, href="language=fr")
        resp_fr = resp_tmp.follow()
        html_fr = resp_fr.html
        news_fr = html_fr.select('a[href$="/getitfixed/issues/new"]')
        assert 1 == len(news_fr)
        assert ["Déclarer un problème"] == list(news_fr[0].stripped_strings)
