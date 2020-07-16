import pytest
import re
import datetime
from random import randrange

from c2cgeoform.testing.views import AbstractViewsTests

from getitfixed.models.getitfixed import (
    Category,
    Issue,
    Type,
    STATUS_VALIDATED,
    STATUS_NEW,
)
from getitfixed.views.private.semi_private_issues import IssueViews as IssuePrivateViews

from unittest.mock import patch, call, ANY

STATUSES = [STATUS_VALIDATED, STATUS_NEW]


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
                icon="meme{}.gif".format(i),
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
                status=STATUSES[i % 2],
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
        self.get(test_app, status=200)

    def test_geojson(self, test_app):
        resp = self.get(test_app, "/geojson.json", status=200)
        # We do not show new (not validated) issues
        assert 5 == len(resp.json["features"])

    @patch("getitfixed.views.public.issues.send_email")
    def test_new_then_save(self, send_email, dbsession, test_app, issue_test_data):
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
            IssuePrivateViews.MSG_COL["submit_ok"]
            == resp.follow().html.find("div", {"class": "msg-lbl"}).getText()
        )

        hash_ = re.match(
            r"http://localhost/getitfixed/private/issues/(.*)\?msg_col=submit_ok", resp.location
        ).group(1)

        obj = dbsession.query(Issue).filter(Issue.hash == hash_).one()
        assert datetime.date.today() == obj.request_date
        assert issue_test_data["types"][0] is obj.type
        assert "Description" == obj.description
        assert "234 long street" == obj.localisation
        assert "Andreas" == obj.firstname
        assert "Ford" == obj.lastname
        assert "04 58 48 20 00" == obj.phone
        assert "andreas.ford@domain.net" == obj.email

        assert 2 == send_email.call_count
        assert send_email.mock_calls[0] == call(
            request=ANY,
            to='andreas.ford@domain.net',
            template_name='new_issue_email',
            template_kwargs={
                'username': 'Andreas Ford',
                'issue': obj,
                'issue-link': 'http://localhost/getitfixed/private/issues/{}'.format(obj.hash),
            },
        )
        assert send_email.mock_calls[1] == call(
            request=ANY,
            to='0.is@abit.ch',
            template_name='admin_new_issue_email',
            template_kwargs={
                'username': 'Andreas Ford',
                'issue': obj,
                'issue-link': 'http://localhost/getitfixed_admin/issues/{}'.format(obj.hash),
            },
        )

    def test_open(self, dbsession, test_app, issue_test_data):
        issue = dbsession.query(Issue).first()
        resp = test_app.get("/getitfixed/issues/{}".format(issue.id), status=200)
        self._check_mapping(
            resp.html.select("form")[0],
            [
                {"name": "description", "value": issue.description, "readonly": True},
                {"name": "localisation", "value": issue.localisation, "readonly": True},
            ],
        )

    def test_open_new(self, dbsession, test_app, issue_test_data):
        issue = issue_test_data["issues"][0]
        issue.status = STATUS_NEW
        dbsession.flush()
        test_app.get("/getitfixed/issues/{}".format(issue.id), status=404)

    def test_open_private(self, dbsession, test_app, issue_test_data):
        issue = issue_test_data["issues"][0]
        issue.private = True
        dbsession.flush()
        test_app.get("/getitfixed/issues/{}".format(issue.id), status=404)
