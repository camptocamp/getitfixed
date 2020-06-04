import pytest
from random import randrange

from c2cgeoform.testing.views import AbstractViewsTests

from getitfixed.models.getitfixed import Category, Event, Issue, Type
from unittest.mock import patch, call, ANY


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("dbsession", "transact")
def issue_test_data(dbsession, transact):
    del transact

    categories = []
    for i in range(5):
        categories.append(
            Category(
                label_en="Category «{}»".format(i),
                label_fr="Catégorie «{}»".format(i),
                email="{}.is@abit.ch".format(i),
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
            )
        )
    dbsession.add_all(types)

    issues = []
    for i in range(0, 10):
        issues.append(
            Issue(
                type=types[i % 15],
                description="{} truite sauvage".format(i),
                localisation="{} rue du pont".format(i),
                firstname="Firstname{}".format(i),
                lastname="Lastname{}".format(i),
                phone="0{} {:02} {:02} {:02} {:02}".format(
                    randrange(1, 10), *[randrange(100) for i in range(4)]
                ),
                email="firstname{0}.lastname{0}@domain.net".format(i),
            )
        )
    dbsession.add_all(issues)

    dbsession.flush()

    yield {"categories": categories, "types": types, "issues": issues}


@pytest.mark.usefixtures("issue_test_data", "test_app")
class TestAdminIssueViews(AbstractViewsTests):

    _prefix = "/getitfixed_admin/issues"

    def test_index(self, test_app):
        resp = self.get(test_app, status=200)

        expected = [
            ("actions", "", "false"),
            ("id", "Identifier", "true"),
            ("status", "Status", "true"),
            ("request_date", "Request date", "true"),
            ("type_id", "Type", "true"),
            ("description", "Description of the problem", "true"),
            ("localisation", "Localisation", "true"),
            ("firstname", "Firstname", "true"),
            ("lastname", "Lastname", "true"),
            ("phone", "Phone", "true"),
            ("email", "Email", "true"),
        ]
        self.check_grid_headers(resp, expected)

    def test_grid(self, test_app, dbsession):
        json = self.check_search(
            test_app, limit=10, sort="identifier", order="asc", total=10
        )
        assert 10 == len(json["rows"])
        assert 10 == json["total"]

        row = json["rows"][5]
        obj = dbsession.query(Issue).get(row["id"])
        assert obj.hash == row["_id_"]
        assert obj.request_date.isoformat() == row["request_date"]
        assert obj.description == row["description"]

    def test_select_category(self, test_app):
        json = self.check_search(
            test_app, limit=10, sort="identifier", order="asc", total=0, category=8
        )
        assert 0 == len(json["rows"])
        assert 0 == json["total"]

    def test_set_private(self, test_app, issue_test_data):
        issue = issue_test_data["issues"][0]
        issue.private = False
        resp = test_app.post("/getitfixed_admin/issues/{}/set_private".format(issue.hash), status=200)
        assert resp.json["success"]
        assert (
            "http://localhost/getitfixed_admin/issues/{}?msg_col=submit_ok".format(issue.hash)
            == resp.json["redirect"]
        )
        assert issue.private

    def test_set_public(self, test_app, issue_test_data):
        issue = issue_test_data["issues"][0]
        issue.public = False
        resp = test_app.post("/getitfixed_admin/issues/{}/set_public".format(issue.hash), status=200)
        assert resp.json["success"]
        assert (
            "http://localhost/getitfixed_admin/issues/{}?msg_col=submit_ok".format(issue.hash)
            == resp.json["redirect"]
        )
        assert not issue.private

    @patch("getitfixed.views.admin.events.send_email")
    def test_edit_then_post_comment(
        self, send_email, test_app, issue_test_data, dbsession
    ):
        issue = issue_test_data["issues"][0]
        resp = self.get(test_app, "/{}".format(issue.hash), status=200)

        self._check_mapping(
            resp.html.select("form")[0],
            [
                {"name": "id", "value": str(issue.id), "hidden": True},
                {"name": "type_id", "value": issue.type.label_en, "readonly": True},
                {"name": "description", "value": issue.description, "readonly": True},
                {"name": "description", "value": issue.description, "readonly": True},
                {"name": "localisation", "value": issue.localisation, "readonly": True},
                # Position
                # Photo
                {"name": "firstname", "value": issue.firstname, "readonly": True},
                {"name": "lastname", "value": issue.lastname, "readonly": True},
                {"name": "phone", "value": issue.phone, "readonly": True},
                {"name": "email", "value": issue.email, "readonly": True},
            ],
        )

        form = resp.forms["new_event_form"]
        assert "" == form["id"].value
        assert str(issue.id) == form["issue_id"].value
        assert issue.status == form["status"].value
        assert "" == form["comment"].value

        form["status"].value = "in_progress"
        form["comment"].value = "This is a comment"

        resp = form.submit("submit", status=302)

        assert (
            "http://localhost/getitfixed_admin/issues/{}#existing_events_form".format(issue.hash)
            == resp.location
        )

        obj = (
            dbsession.query(Event)
            .filter(Event.issue_id == issue.id)
            .order_by(Event.date.desc())
            .first()
        )

        assert "in_progress" == obj.status
        assert "This is a comment" == obj.comment

        assert "in_progress" == issue.status

        assert send_email.call_count == 1
        assert send_email.mock_calls[0] == call(
            request=ANY,
            to='firstname0.lastname0@domain.net',
            template_name='update_issue_email',
            template_kwargs={
                'username': 'Firstname0 Lastname0',
                'issue': obj.issue,
                'event': obj,
                'issue-link': 'http://localhost/getitfixed/private/issues/{}#existing_events_form'.format(obj.issue.hash),
            },
        )

    @patch("getitfixed.emails.email_service.smtplib.SMTP")
    def test_edit_then_post_private_comment(
        self, smtp_mock, test_app, issue_test_data, dbsession
    ):
        issue = issue_test_data["issues"][0]
        resp = self.get(test_app, "/{}".format(issue.hash), status=200)

        self._check_mapping(
            resp.html.select("form")[0],
            [
                {"name": "id", "value": str(issue.id), "hidden": True},
                {"name": "type_id", "value": issue.type.label_en, "readonly": True},
                {"name": "description", "value": issue.description, "readonly": True},
                {"name": "localisation", "value": issue.localisation, "readonly": True},
                # Position
                # Photo
                {"name": "firstname", "value": issue.firstname, "readonly": True},
                {"name": "lastname", "value": issue.lastname, "readonly": True},
                {"name": "phone", "value": issue.phone, "readonly": True},
                {"name": "email", "value": issue.email, "readonly": True},
            ],
        )

        form = resp.forms["new_event_form"]
        assert "" == form["id"].value
        assert str(issue.id) == form["issue_id"].value
        assert issue.status == form["status"].value
        assert "" == form["comment"].value

        form["status"].value = "in_progress"
        form["comment"].value = "This is a private comment"
        form["private"].value = True

        resp = form.submit("submit", status=302)

        assert (
            "http://localhost/getitfixed_admin/issues/{}#existing_events_form".format(issue.hash)
            == resp.location
        )

        obj = (
            dbsession.query(Event)
            .filter(Event.issue_id == issue.id)
            .order_by(Event.date.desc())
            .first()
        )

        assert "This is a private comment" == obj.comment
        assert True is obj.private

        assert "in_progress" == issue.status
        assert smtp_mock.call_count == 0
