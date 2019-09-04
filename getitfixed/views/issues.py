from pyramid.view import view_config
from pyramid.view import view_defaults
from functools import partial

from sqlalchemy.orm import subqueryload

from colander import SchemaNode, Int
from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.ext.deform_ext import RelationSelectWidget
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.models.getitfixed import (
    Category,
    Issue,
    Type,
)
from getitfixed.i18n import _

_list_field = partial(ListField, Issue)

new_schema = GeoFormSchemaNode(
    Issue,
    excludes=[
        'request_date',
    ])

new_schema.add_before(
    'type_id',
    SchemaNode(
        Int(),
        name='category_id',
        title='Category',
        widget=RelationSelectWidget(
            Category,
            'id',
            'label_fr',
            order_by='label_fr'
        ),
    )
)

follow_schema = GeoFormSchemaNode(
    Issue,
    includes=['request_date',
              'type_id',
              'description',
              'localisation',
              'geometry',
              ])


def get_types(request):
    return {
        "fields": ['category_id', 'type_id'],
        "values": [
            dict(id=o.id, cat=o.category_id, label=o.label_fr)
            for o in request.dbsession.query(Type)
        ]}


@view_defaults(match_param='table=issues')
class IssueViews(AbstractViews):

    _model = Issue
    _base_schema = new_schema
    _id_field = 'hash'

    _list_fields = [
        _list_field('id'),
        _list_field('request_date'),
        _list_field('type_id',
                    renderer=lambda issue: issue.type.label_fr,
                    sort_column=Type.label_fr,
                    filter_column=Type.label_fr),
        _list_field('description'),
        _list_field('localisation'),
        _list_field('firstname'),
        _list_field('lastname'),
        _list_field('phone'),
        _list_field('email'),
    ]

    MSG_COL = {
        'submit_ok': _('Thank you for your report, '
                       'it has been registered with following details, '
                       'and will be treated as soon as possible.'),
        'copy_ok': _('Please check that the copy fits before submitting.'),
    }

    def _base_query(self):
        return super()._base_query(). \
            outerjoin(Issue.type). \
            options(subqueryload(Issue.type))

    @view_config(route_name='c2cgeoform_index',
                 renderer='../templates/index.jinja2')
    def index(self):
        return super().index()

    @view_config(route_name='c2cgeoform_grid',
                 renderer='json')
    def grid(self):
        return super().grid()

    def _item_actions(self, item):
        return []

    @view_config(route_name='c2cgeoform_item',
                 request_method='GET',
                 renderer='../templates/edit.jinja2')
    def edit(self):
        if self._is_new():
            base_edit = super().edit()
            base_edit['form_render_kwargs'].update(
                    {"deps": get_types(self._request)})
            return base_edit
        else:
            return super().edit(schema=follow_schema,
                                readonly=True)

    # For development/testing purpose
    @view_config(route_name='c2cgeoform_item_duplicate',
                 request_method='GET',
                 renderer='../templates/edit.jinja2')
    def duplicate(self):
        base_duplicate = super().duplicate()
        base_duplicate['form_render_kwargs'].update(
                {"deps": get_types(self._request)})
        return base_duplicate

    @view_config(route_name='c2cgeoform_item',
                 request_method='POST',
                 renderer='../templates/edit.jinja2')
    def save(self):
        return super().save()
