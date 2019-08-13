import pytest
import re
from datetime import datetime
from pyramid.testing import DummyRequest
from getitfixed.models.getitfixed import Issue
from getitfixed.views.issues import IssueViews


@pytest.fixture(scope='function')
@pytest.mark.usefixtures('dbsession', 'transact')
def issue_test_data(dbsession, transact):
    del transact
    issues = []
    for i in range(0, 10):
        issue = Issue()
        issue.description = '{} truite sauvage'.format(i)
        issue.request_date = datetime.now()
        issues.append(issue)
        dbsession.add(issue)

    dbsession.flush()

    yield {
        'issues': issues
    }


@pytest.mark.usefixtures("issue_test_data", "test_app")
class TestIssueViews():

    def _obj_by_desc(self, dbsession, desc):
        return dbsession.query(Issue). \
            filter(Issue.description == desc). \
            one_or_none()

    def test_index(self, test_app):
        resp = test_app.get("/getitfixed/issues", status=200)

        resp_tmp = resp.click(verbose=True, href="language=en")
        resp_en = resp_tmp.follow()
        html_en = resp_en.html
        news_en = html_en.select('a[href$="/getitfixed/issues/new"]')
        assert 1 == len(news_en)
        assert "New" == news_en[0].string

        reference_numbers = html_en.select("th[data-field=id]")
        assert 1 == len(reference_numbers)
        assert "Identifier" == reference_numbers[0].string

        resp_tmp = resp_en.click(verbose=True, href="language=fr")
        resp_fr = resp_tmp.follow()
        html_fr = resp_fr.html
        news_fr = html_fr.select('a[href$="/getitfixed/issues/new"]')
        assert 1 == len(news_fr)
        assert "Nouveau" == news_fr[0].string

    def test_grid(self, test_app, dbsession):
        json = test_app.post(
            "/getitfixed/issues/grid.json",
            params={
                "offset": 0,
                "limit": 10,
                "sort": "identifier",
                "order": "asc"
            },
            status=200
        ).json
        assert 10 == len(json["rows"])
        assert 10 == json["total"]

        row = json["rows"][5]
        exc = dbsession.query(Issue).get(row["id"])
        assert exc.hash == row["_id_"]
        assert exc.request_date.strftime("%Y-%m-%d %H:%M:%S.%f") == row["request_date"]
        assert exc.description == row["description"]

    '''def test_grid_filter(self, test_app):
        json = test_app.post(
            "/getitfixed/issue/grid.json",
            params={
                "offset": 0,
                "limit": 10,
                "sort": "id",
                "order": "asc",
                "search": "Poule"
            },
            status=200
        ).json

        assert 10 == len(json["rows"])
        assert 50 == json["total"]

        row = json["rows"][0]
        assert "Poule" in row["description"]

    def test_edit_then_save(self, dbsession, test_app):
        obj = dbsession.query(Issue).first()
        resp = test_app.get("/getitfixed/issues/{}".format(obj.id), status=200)

        form = resp.form
        assert str(obj.id) == form['id'].value
        assert obj.hash == form['hash'].value
        assert str(obj.request_date) == form['date'].value
        assert obj.description == form["description"].value
        # assert obj.photos == form["photos"].value

        form["description"] = "New description"

        resp = form.submit("submit")

        dbsession.expire(obj)

        assert obj.hash == re.match(
            'http://localhost/getitfixed/issues/(.*)\?msg_col=submit_ok',
            resp.location).group(1)

        assert "New description" == obj.description

        assert 'Your submission has been taken into account.' == \
               resp.follow().html.find('div', {'class': 'msg-lbl'}).getText()'''

    def test_edit_new_then_save(self, dbsession, test_app):
        resp = test_app.get("/getitfixed/issues/new", status=200)

        form = resp.form
        assert '' == form['id'].value
        assert '' == form['hash'].value
        assert '' == form['date'].value
        assert '' == form["description"].value

        form["description"] = "Description"

        resp = form.submit("submit")

        obj = self._obj_by_desc(dbsession, "Description")

        assert obj.hash == re.match(
            'http://localhost/getitfixed/issues/(.*)\?msg_col=submit_ok',
            resp.location).group(1)

        assert "Description" == obj.description

        assert 'Your submission has been taken into account.' == \
            resp.follow().html.find('div', {'class': 'msg-lbl'}).getText()
