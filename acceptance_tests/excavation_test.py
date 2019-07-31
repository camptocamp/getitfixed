import pytest
import re
from pyramid.testing import DummyRequest
from getitfixed.models.c2cgeoform_demo import Excavation, Situation
from getitfixed.views.excavation import ExcavationViews


@pytest.mark.usefixtures("transact", "test_app")
class TestExcavationViews():
    def check_checkboxes_list_widget(self, resp, all_situations, excavation):
        form_group = resp.html.select_one('.item-situations')
        situations_labels = form_group.select('.checkbox label')
        for i, situation in enumerate(all_situations):
            label = situations_labels[i]
            input = label.select_one('input')
            assert [situation.name] == list(label.stripped_strings)
            assert str(situation.id) == input['value']
            if situation in excavation.situations:
                assert 'True' == input['checked']
                assert resp.form.get('situations', index=i).checked
            else:
                assert 'checked' not in input
                assert not resp.form.get('situations', index=i).checked

    def _excavation_by_desc(self, dbsession, desc):
        return dbsession.query(Excavation). \
            filter(Excavation.description == desc). \
            one_or_none()

    def _excavation_by_ref(self, dbsession, ref):
        return dbsession.query(Excavation). \
            filter(Excavation.reference_number == ref). \
            one_or_none()

    def test_index(self, test_app):
        resp = test_app.get("/excavations", status=200)

        resp_tmp = resp.click(verbose=True, href="language=en")
        resp_en = resp_tmp.follow()
        html_en = resp_en.html
        news_en = html_en.select('a[href$="/excavations/new"]')
        assert 1 == len(news_en)
        assert "New" == news_en[0].string

        reference_numbers = html_en.select("th[data-field=reference_number]")
        assert 1 == len(reference_numbers)
        assert "Reference Number" == reference_numbers[0].string

        resp_tmp = resp_en.click(verbose=True, href="language=fr")
        resp_fr = resp_tmp.follow()
        html_fr = resp_fr.html
        news_fr = html_fr.select('a[href$="/excavations/new"]')
        assert 1 == len(news_fr)
        assert "Nouveau" == news_fr[0].string

    def test_grid(self, test_app, dbsession):
        json = test_app.post(
            "/excavations/grid.json",
            params={
                "offset": 0,
                "limit": 10,
                "sort": "reference_number",
                "order": "asc"
            },
            status=200
        ).json

        assert 10 == len(json["rows"])
        assert 100 == json["total"]

        row = json["rows"][5]
        exc = self._excavation_by_ref(dbsession, row["reference_number"])
        assert exc.hash == row["_id_"]
        assert exc.description == row["description"]
        assert exc.location_town == row["location_town"]
        assert exc.request_date.strftime("%Y-%m-%d") == row["request_date"]
        assert exc.responsible_company == row["responsible_company"]
        assert ", ".join([situation.name for situation in exc.situations]) == row["situations"]

    def test_grid_filter(self, test_app):
        json = test_app.post(
            "/excavations/grid.json",
            params={
                "offset": 0,
                "limit": 10,
                "sort": "reference_number",
                "order": "asc",
                "search": "Road"
            },
            status=200
        ).json

        assert 10 == len(json["rows"])
        assert 49 == json["total"]

        row = json["rows"][0]
        assert "Road" in row["situations"]

    def test_edit_then_save(self, dbsession, test_app):
        exc = self._excavation_by_ref(dbsession, "ref0001")
        resp = test_app.get("/excavations/{}".format(exc.hash), status=200)

        form = resp.form
        assert exc.reference_number == form['reference_number'].value
        assert exc.hash == form['hash'].value
        assert str(exc.id) == form.fields.get('id')[0].value
        assert str(exc.request_date) == form['date'].value
        assert exc.description == form["description"].value
        assert exc.motif == form["motif"].value
        assert exc.contact_persons[0].first_name == form["first_name"].value
        assert exc.contact_persons[0].last_name == form["last_name"].value
        assert str(exc.contact_persons[0].id) == form.fields.get('id')[1].value
        assert str(exc.contact_persons[0].permission_id) == form['permission_id'].value
        assert exc.contact_persons[0].permission_id == exc.id
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
        assert "true" if exc.validated else "false" == form["validated"].value
        assert str(exc.work_footprint or "") == form["work_footprint"].value
        # assert form["photos"].value == exc.photos

        all_situations = dbsession.query(Situation).order_by(Situation.name).all()
        self.check_checkboxes_list_widget(resp, all_situations, exc)

        form["description"] = "New description"
        form["motif"] = "New motif"
        form["location_district_id"] = 4  # name="La Claie-aux-Moines"
        form["location_street"] = "rue des écoles"
        form["location_postal_code"] = '73000'
        form["location_town"] = "Beçanson"
        form["address_id"] = 4  # label="Lugano"
        form["location_position"] = ''
        form["responsible_title"] = "mr"
        form["responsible_name"] = "lapin"
        form["responsible_first_name"] = "malin"
        form["responsible_mobile"] = "06.75.65.83"
        form["responsible_mail"] = "lapin.malin@lugano.ch"
        form["responsible_company"] = "csc"
        form["validated"] = False
        form["work_footprint"] = ''
        form["first_name"] = 'Raoul'
        form["last_name"] = 'Wolffoni'


        form["situations"] = ['3', '4', '5']  # RelationCheckBoxListWidget

        resp = form.submit("submit")

        dbsession.expire(exc)

        assert exc.hash == re.match(
            'http://localhost/excavations/(.*)\?msg_col=submit_ok',
            resp.location).group(1)

        assert "New description" == exc.description
        assert "New motif" == exc.motif
        assert 4 == exc.location_district_id  # name="La Claie-aux-Moines"
        assert "rue des écoles" == exc.location_street
        assert "73000" == exc.location_postal_code
        assert "Beçanson" == exc.location_town
        assert 4 == exc.address_id  # label="Lugano"
        assert None == exc.location_position
        assert "mr" == exc.responsible_title
        assert "lapin" == exc.responsible_name
        assert "malin" == exc.responsible_first_name
        assert "06.75.65.83" == exc.responsible_mobile
        assert "lapin.malin@lugano.ch" == exc.responsible_mail
        assert "csc" == exc.responsible_company
        assert "Raoul" == exc.contact_persons[0].first_name
        assert False == exc.validated
        assert None == exc.work_footprint

        situation_ids = [situation.id for situation
                          in exc.situations]
        assert set([3, 4, 5]) == set(situation_ids)
        assert 'Your submission has been taken into account.' == \
            resp.follow().html.find('div', {'class': 'msg-lbl'}).getText()

    def test_edit_new_then_save(self, dbsession, test_app):
        resp = test_app.get("/excavations/new", status=200)

        form = resp.form
        assert '' == form['reference_number'].value
        assert '' == form['hash'].value
        assert '' == form.fields.get('id')[0].value
        assert '' == form['date'].value
        assert '' == form["description"].value
        assert '' == form["motif"].value
        assert form.fields.get('first_name') is None # no contact_persons
        assert '' == form["location_district_id"].value
        assert '' == form["location_street"].value
        assert '' == form["location_postal_code"].value
        assert '' == form["location_town"].value
        assert '' == form["address_id"].value
        assert '' == form["location_position"].value
        assert '' == form["responsible_title"].value
        assert '' == form["responsible_name"].value
        assert '' == form["responsible_first_name"].value
        assert '' == form["responsible_mobile"].value
        assert '' == form["responsible_mail"].value
        assert '' == form["responsible_company"].value
        assert None == form["validated"].value
        assert '' == form["work_footprint"].value
        # assert form["photos"].value == exc.photos

        all_situations = dbsession.query(Situation).order_by(Situation.name).all()
        self.check_checkboxes_list_widget(resp, all_situations, Excavation())

        form["description"] = "Description"
        form["motif"] = "Motif"
        form["location_district_id"] = 4  # name="La Claie-aux-Moines"
        form["location_street"] = "rue des écoles"
        form["location_postal_code"] = '73000'
        form["location_town"] = "Beçanson"
        form["address_id"] = 4  # label="Lugano"
        form["location_position"] = ''
        form["responsible_title"] = "mr"
        form["responsible_name"] = "lapin"
        form["responsible_first_name"] = "malin"
        form["responsible_mobile"] = "06.75.65.83"
        form["responsible_mail"] = "lapin.malin@lugano.ch"
        form["responsible_company"] = "csc"
        form["validated"] = False
        form["work_footprint"] = ''
        form['situations'] = ['3', '4', '5']  # RelationCheckBoxListWidget

        resp = form.submit("submit")

        exc = self._excavation_by_desc(dbsession, "Description")

        assert exc.hash == re.match(
            'http://localhost/excavations/(.*)\?msg_col=submit_ok',
            resp.location).group(1)

        assert "Description" == exc.description
        assert "Motif" == exc.motif
        assert 4 == exc.location_district_id  # name="La Claie-aux-Moines"
        assert "rue des écoles" == exc.location_street
        assert "73000" == exc.location_postal_code
        assert "Beçanson" == exc.location_town
        assert 4 == exc.address_id  # label="Lugano"
        assert None == exc.location_position
        assert "mr" == exc.responsible_title
        assert "lapin" == exc.responsible_name
        assert "malin" == exc.responsible_first_name
        assert "06.75.65.83" == exc.responsible_mobile
        assert "lapin.malin@lugano.ch" == exc.responsible_mail
        assert "csc" == exc.responsible_company
        assert False == exc.validated
        assert None == exc.work_footprint

        situation_ids = [situation.id for situation in exc.situations]
        assert set([3, 4, 5]) == set(situation_ids)
        assert 'Your submission has been taken into account.' == \
            resp.follow().html.find('div', {'class': 'msg-lbl'}).getText()

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
