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
class TestSemiPrivateIssueViews(AbstractViewsTests):

    _prefix = "/getitfixed/private/issues"

    @patch("getitfixed.views.private.semi_private_events.send_email")
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

        assert send_email.call_count == 1
        assert send_email.mock_calls[0] == call(
            request=ANY,
            to='0.is@abit.ch',
            template_name='update_issue_email',
            template_kwargs={
                'username': 'Firstname0 Lastname0',
                'issue': obj.issue,
                'event': obj,
                'issue-link': 'http://localhost/getitfixed_admin/issues/{}#existing_events_form'.format(obj.issue.hash),
            },
        )

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

        resp = form.submit("submit", status=200)

        assert "http://localhost/getitfixed/events/new" == resp.request.path_url
        assert smtp_mock.call_count == 0
