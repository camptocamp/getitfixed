import pytest
import re
import datetime
from random import randrange

from c2cgeoform.testing.views import AbstractViewsTests

from getitfixed.models.getitfixed import Category, Event, Issue, Type
from getitfixed.views.issues import IssueViews

from unittest.mock import patch


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
class TestIssueViews(AbstractViewsTests):

    _prefix = "/getitfixed/issues"

    def _obj_by_hash(self, dbsession, hash_):
        return dbsession.query(Issue).filter(Issue.hash == hash_).one_or_none()

    def test_index(self, test_app):
        resp = self.get(test_app, status=200)

        expected = [
            ("description", "Description", "true"),
            ("type_id", "Type", "true"),
            ("localisation", "Localisation", "true"),
            ("request_date", "Request date", "true"),
        ]
        self.check_grid_headers(resp, expected, check_actions=False)

    def test_grid(self, test_app, dbsession):
        json = self.check_search(
            test_app, limit=10, sort="identifier", order="asc", total=10
        )
        assert 10 == len(json["rows"])
        assert 10 == json["total"]

        row = json["rows"][5]
        obj = dbsession.query(Issue).filter(Issue.id == row["_id_"]).first()
        assert obj.id == int(row["_id_"])
        assert obj.description in row["description"]

    @patch("getitfixed.emails.email_service.smtplib.SMTP")
    def test_new_then_save(self, smtp_mock, dbsession, test_app, issue_test_data):
        resp = test_app.get("/getitfixed/issues/new", status=200)

        form = resp.form
        assert "" == form["id"].value
        assert "" == form["type_id"].value
        assert "" == form["description"].value
        assert "" == form["localisation"].value
        assert "" == form["firstname"].value
        assert "" == form["lastname"].value
        assert "" == form["phone"].value
        assert "" == form["email"].value

        form["type_id"] = str(issue_test_data["types"][0].id)
        form["description"] = "Description"
        form["localisation"] = "234 long street"
        form["firstname"] = "Andreas"
        form["lastname"] = "Ford"
        form["phone"] = "04 58 48 20 00"
        form["email"] = "andreas.ford@domain.net"

        resp = form.submit("submit", status=302)

        assert (
            IssueViews.MSG_COL["submit_ok"]
            == resp.follow().html.find("div", {"class": "msg-lbl"}).getText()
        )

        id_ = re.match(
            r"http://localhost/getitfixed/issues/(.*)\?msg_col=submit_ok", resp.location
        ).group(1)

        obj = dbsession.query(Issue).get(id_)
        assert datetime.date.today() == obj.request_date
        assert issue_test_data["types"][0] is obj.type
        assert "Description" == obj.description
        assert "234 long street" == obj.localisation
        assert "Andreas" == obj.firstname
        assert "Ford" == obj.lastname
        assert "04 58 48 20 00" == obj.phone
        assert "andreas.ford@domain.net" == obj.email

        assert smtp_mock.called, "method should have been called"
        assert smtp_mock.call_count == 2


@pytest.mark.usefixtures("issue_test_data", "test_app")
class TestSemiPrivateIssueViews(AbstractViewsTests):

    _prefix = "http://localhost/getitfixed/private/issues"

    @patch("getitfixed.emails.email_service.smtplib.SMTP")
    def test_edit_then_post_comment(
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
                {"name": "description", "value": issue.description, "readonly": True},
                {"name": "localisation", "value": issue.localisation, "readonly": True},
            ],
        )

        form = resp.forms["new_event_form"]
        assert "" == form["id"].value
        assert str(issue.id) == form["issue_id"].value
        assert "" == form["comment"].value

        form["comment"].value = "This is a user comment"

        resp = form.submit("submit", status=302)

        assert (
            "http://localhost/getitfixed/private/issues/{}#existing_events_form".format(
                issue.hash
            )
            == resp.location
        )

        obj = (
            dbsession.query(Event)
            .filter(Event.issue_id == issue.id)
            .order_by(Event.date.desc())
            .first()
        )

        assert "new" == obj.status
        assert "This is a user comment" == obj.comment
        assert "new" == issue.status
        assert smtp_mock.call_count == 1

    @patch("getitfixed.emails.email_service.smtplib.SMTP")
    def test_edit_then_post_empty_comment(
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
                {"name": "description", "value": issue.description, "readonly": True},
                {"name": "localisation", "value": issue.localisation, "readonly": True},
            ],
        )

        form = resp.forms["new_event_form"]
        assert "" == form["id"].value
        assert str(issue.id) == form["issue_id"].value
        assert "" == form["comment"].value

        form["comment"].value = ""

        resp = form.submit("submit", status=200)

        assert "http://localhost/getitfixed/events/new" == resp.request.path_url
        assert smtp_mock.call_count == 0
