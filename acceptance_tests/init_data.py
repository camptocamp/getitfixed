import pytest
from random import randrange

from getitfixed.models.getitfixed import Category, Event, Issue, Type


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
