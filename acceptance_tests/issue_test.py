import pytest
import re
import datetime

from getitfixed.models.getitfixed import (
    Category,
    Issue,
    Type,
)


@pytest.fixture(scope='function')
@pytest.mark.usefixtures('dbsession', 'transact')
def issue_test_data(dbsession, transact):
    del transact

    categories = []
    for i in range(5):
        categories.append(Category(
            label_fr='Catégorie «{}»'.format(i)
        ))
    dbsession.add_all(categories)

    types = []
    for i in range(15):
        types.append(Type(
            label_fr='Type «{}»'.format(i),
            category=categories[i % 3]
        ))
    dbsession.add_all(types)

    issues = []
    for i in range(0, 10):
        issue = Issue()
        issue.type = types[i % 15]
        issue.description = '{} truite sauvage'.format(i)
        issues.append(issue)
    dbsession.add_all(issues)

    dbsession.flush()

    yield {
        'categories': categories,
        'types': types,
        'issues': issues,
    }


@pytest.mark.usefixtures('issue_test_data', 'test_app')
class TestIssueViews():

    def _obj_by_hash(self, dbsession, hash_):
        return dbsession.query(Issue). \
            filter(Issue.hash == hash_). \
            one_or_none()

    def test_index(self, test_app):
        resp = test_app.get('/getitfixed/issues', status=200)

        resp_tmp = resp.click(verbose=True, href='language=en')
        resp_en = resp_tmp.follow()
        html_en = resp_en.html
        news_en = html_en.select('a[href$="/getitfixed/issues/new"]')
        assert 1 == len(news_en)
        assert 'New' == news_en[0].string

        reference_numbers = html_en.select('th[data-field=id]')
        assert 1 == len(reference_numbers)
        assert 'Identifier' == reference_numbers[0].string

        resp_tmp = resp_en.click(verbose=True, href='language=fr')
        resp_fr = resp_tmp.follow()
        html_fr = resp_fr.html
        news_fr = html_fr.select('a[href$="/getitfixed/issues/new"]')
        assert 1 == len(news_fr)
        assert 'Nouveau' == news_fr[0].string

    def test_grid(self, test_app, dbsession):
        json = test_app.post(
            '/getitfixed/issues/grid.json',
            params={
                'offset': 0,
                'limit': 10,
                'sort': 'identifier',
                'order': 'asc'
            },
            status=200
        ).json
        assert 10 == len(json['rows'])
        assert 10 == json['total']

        row = json['rows'][5]
        obj = dbsession.query(Issue).get(row['id'])
        assert obj.hash == row['_id_']
        assert obj.request_date.isoformat() == row['request_date']
        assert obj.description == row['description']

    def test_new_then_save(self, dbsession, test_app, issue_test_data):
        resp = test_app.get('/getitfixed/issues/new', status=200)

        form = resp.form
        assert '' == form['id'].value
        assert '' == form['type_id'].value
        assert '' == form['description'].value

        form['type_id'] = str(issue_test_data['types'][0].id)
        form['description'] = 'Description'

        resp = form.submit('submit', status=302)

        hash_ = re.match(
            r'http://localhost/getitfixed/issues/(.*)\?msg_col=submit_ok',
            resp.location).group(1)

        obj = self._obj_by_hash(dbsession, hash_)
        assert datetime.date.today() == obj.request_date
        assert 'Description' == obj.description
        assert issue_test_data['types'][0] is obj.type

        assert 'Your submission has been taken into account.' == \
            resp.follow().html.find('div', {'class': 'msg-lbl'}).getText()
