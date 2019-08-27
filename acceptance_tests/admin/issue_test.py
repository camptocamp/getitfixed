import pytest

from c2cgeoform.testing.views import AbstractViewsTests

from getitfixed.models.getitfixed import (
    Issue,
)
from ..issue_test import issue_test_data  # noqa


@pytest.mark.usefixtures('issue_test_data', 'test_app')
class TestAdminIssueViews(AbstractViewsTests):

    _prefix = '/admin/issues'

    def test_index(self, test_app):
        resp = self.get(test_app, status=200)

        self.check_left_menu(resp, 'Issues')

        expected = [('actions', '', 'false'),
                    ('id', 'Identifier', 'true'),
                    ('request_date', 'Request date', 'true'),
                    ('type_id', 'Type', 'true'),
                    ('description', 'Description', 'true'),
                    ('localisation', 'Localisation', 'true'),
                    ('firstname', 'Firstname', 'true'),
                    ('lastname', 'Lastname', 'true'),
                    ('phone', 'Phone', 'true'),
                    ('email', 'Email', 'true'),
                    ]
        self.check_grid_headers(resp, expected)

    def test_grid(self, test_app, dbsession):
        json = self.check_search(test_app,
                                 limit=10,
                                 sort='identifier',
                                 order='asc',
                                 total=10)
        assert 10 == len(json['rows'])
        assert 10 == json['total']

        row = json['rows'][5]
        obj = dbsession.query(Issue).get(row['id'])
        assert obj.hash == row['_id_']
        assert obj.request_date.isoformat() == row['request_date']
        assert obj.description == row['description']

    def test_edit(self, test_app, issue_test_data, dbsession):
        issue = issue_test_data['issues'][0]
        resp = self.get(test_app, '/{}'.format(issue.hash), status=200)
        self._check_mapping(resp.html.select_one('form'), [
            {'name': 'id', 'value': str(issue.id), 'hidden': True},
            {'name': 'type_id', 'value': issue.type.label_en, 'readonly': True},
            {'name': 'description', 'value': issue.description, 'readonly': True},
            {'name': 'description', 'value': issue.description, 'readonly': True},
            {'name': 'localisation', 'value': issue.localisation, 'readonly': True},
            # Position
            # Photo
            {'name': 'firstname', 'value': issue.firstname, 'readonly': True},
            {'name': 'lastname', 'value': issue.lastname, 'readonly': True},
            {'name': 'phone', 'value': issue.phone, 'readonly': True},
            {'name': 'email', 'value': issue.email, 'readonly': True},
            
        ])
