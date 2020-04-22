import pytest

from getitfixed.models.getitfixed import Category, Type, Issue, STATUSES, STATUS_IN_PROGRESS


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("dbsession", "transact")
def issue(dbsession, transact):
    del transact

    category = Category(
        label_en="Category",
        label_fr="Catégorie",
        email="is@abit.ch",
    )

    typ = Type(
        label_en="Type",
        label_fr="Type",
        category=category,
    )

    issue = Issue(
        type=typ,
        description="description",
        localisation="localisation",
        firstname="firstname",
        lastname="lastname",
        phone="0479000000",
        status=STATUS_IN_PROGRESS,
        email="firstname.lastname@domain.net",
    )

    dbsession.add(issue)
    dbsession.flush()

    yield issue


@pytest.mark.usefixtures("issue")
class TestIssue:
    def test_status_i18n(self, issue):
        assert issue.status_de == "In progress"  # FIXME: after de translations are done
        assert issue.status_en == "In progress"
        assert issue.status_fr == "En cours"
