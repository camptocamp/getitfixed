import pytest
import re
from pyramid.testing import DummyRequest
from getitfixed.models.getitfixed import Issue
from getitfixed.views.issues import IssueViews


@pytest.mark.usefixtures("transact", "test_app")
class TestIssueViews():

    def _obj_by_desc(self, dbsession, desc):
        return dbsession.query(Issue). \
            filter(Issue.description == desc). \
            one_or_none()

    def test_index(self, test_app):
        resp = test_app.get("/issues", status=200)

        resp_tmp = resp.click(verbose=True, href="language=en")
        resp_en = resp_tmp.follow()
        html_en = resp_en.html
        news_en = html_en.select('a[href$="/issues/new"]')
        assert 1 == len(news_en)
        assert "New" == news_en[0].string

        reference_numbers = html_en.select("th[data-field=id]")
        assert 1 == len(reference_numbers)
        assert "Identifier" == reference_numbers[0].string

        resp_tmp = resp_en.click(verbose=True, href="language=fr")
        resp_fr = resp_tmp.follow()
        html_fr = resp_fr.html
        news_fr = html_fr.select('a[href$="/issues/new"]')
        assert 1 == len(news_fr)
        assert "Nouveau" == news_fr[0].string

    def test_grid(self, test_app, dbsession):
        json = test_app.post(
            "/issues/grid.json",
            params={
                "offset": 0,
                "limit": 10,
                "sort": "identifier",
                "order": "asc"
            },
            status=200
        ).json

        assert 10 == len(json["rows"])
        assert 100 == json["total"]

        row = json["rows"][5]
        exc = dbsession.query(Issue).get(row["id"])
        assert exc.hash == row["_id_"]
        assert exc.request_date.strftime("%Y-%m-%d") == row["request_date"]
        assert exc.description == row["description"]

    def test_grid_filter(self, test_app):
        json = test_app.post(
            "/issue/grid.json",
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
        resp = test_app.get("/issues/{}".format(obj.id), status=200)

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
            'http://localhost/issues/(.*)\?msg_col=submit_ok',
            resp.location).group(1)

        assert "New description" == obj.description

        assert 'Your submission has been taken into account.' == \
            resp.follow().html.find('div', {'class': 'msg-lbl'}).getText()

    def test_edit_new_then_save(self, dbsession, test_app):
        resp = test_app.get("/issues/new", status=200)

        form = resp.form
        assert '' == form['id'].value
        assert '' == form['hash'].value
        assert '' == form['date'].value
        assert '' == form["description"].value

        form["description"] = "Description"

        resp = form.submit("submit")

        obj = self._obj_by_desc(dbsession, "Description")

        assert obj.hash == re.match(
            'http://localhost/issues/(.*)\?msg_col=submit_ok',
            resp.location).group(1)

        assert "Description" == obj.description

        assert 'Your submission has been taken into account.' == \
            resp.follow().html.find('div', {'class': 'msg-lbl'}).getText()

    '''
    def test_edit_new_then_save_with_missing_field(self, dbsession, test_app):
        resp = test_app.get("/excavations/new", status=200)

        resp = resp.form.submit("submit")

        assert 'There was a problem with your submission' == \
            resp.html.select_one('div[class="error-msg-lbl"]').text
        assert 'Errors have been highlighted below' == \
            resp.html.select_one('div[class="error-msg-detail"]').text
        assert ['Postal Code', 'Street', 'Town'] == \
            sorted([(x.select_one("label").text.strip()) \
            for x in resp.html.select(".has-error")])

    def test_duplicate(self, dbsession, test_app):
        exc = self._excavation_by_ref(dbsession, "ref0001")
        resp = test_app.get("/excavations/{}/duplicate".format(exc.hash), status=200)
        exc = self._excavation_by_ref(dbsession, "ref0001")
        form = resp.form

        assert '' == form['reference_number'].value
        assert '' == form['hash'].value
        assert '' == form.fields.get('id')[0].value
        assert None == form["validated"].value
        assert str(exc.request_date) == form['date'].value
        assert exc.description == form["description"].value
        assert exc.motif == form["motif"].value
        assert str(exc.location_district_id) == form["location_district_id"].value
        assert exc.location_street == form["location_street"].value
        assert exc.location_postal_code == form["location_postal_code"].value
        assert exc.location_town == form["location_town"].value
        assert str(exc.address_id or "") == form["address_id"].value
        assert str(exc.location_position or "") == form["location_position"].value
        assert exc.responsible_title == form["responsible_title"].value
        assert exc.responsible_name == form["responsible_name"].value
        assert exc.responsible_first_name == form["responsible_first_name"].value
        assert exc.responsible_mobile == form["responsible_mobile"].value
        assert exc.responsible_mail == form["responsible_mail"].value
        assert exc.responsible_company == form["responsible_company"].value
        assert str(exc.work_footprint or "") == form["work_footprint"].value
        all_situations = dbsession.query(Situation).order_by(Situation.name).all()
        self.check_checkboxes_list_widget(resp, all_situations, exc)
        assert exc.contact_persons[0].first_name == form["first_name"].value
        assert exc.contact_persons[0].last_name == form["last_name"].value
        assert '' == form.fields.get('id')[1].value
        assert exc.contact_persons[0].id != form.fields.get('id')[1].value
        assert '' == form['permission_id'].value
        assert exc.contact_persons[0].permission_id != form['permission_id'].value

        assert 'Please check that the copy fits before submitting.' == \
            resp.html.find('div', {'class': 'msg-lbl'}).getText()


    def test_unique_validator(self, dbsession, test_app):
        exc = self._excavation_by_ref(dbsession, "ref0001")
        resp = test_app.get("/excavations/{}/duplicate".format(exc.hash), status=200)
        form = resp.form
        form['reference_number'] = exc.reference_number
        resp = form.submit("submit")
        assert 'There was a problem with your submission' == \
            resp.html.select_one('div[class="error-msg-lbl"]').text
        assert 'Errors have been highlighted below' == \
            resp.html.select_one('div[class="error-msg-detail"]').text
        assert '{} is already used.'.format(exc.reference_number) == \
            resp.html.select_one(".has-error").select_one(".help-block").getText()

    def test_delete_success(self, dbsession, test_app):
        exc = self._excavation_by_ref(dbsession, "ref0001")

        resp = test_app.delete("/excavations/{}".format(exc.hash),
            status=200)

        exc = self._excavation_by_ref(dbsession, "ref0001")
        assert None == exc
    '''
