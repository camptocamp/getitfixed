from pyramid.view import view_config
from pyramid.view import view_defaults
from functools import partial

import colander
from c2cgeoform.schema import (
    GeoFormSchemaNode,
)
from c2cgeoform.ext.deform_ext import (
    RelationSelect2Widget,
)
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.models.getitfixed import Issue, Category

_list_field = partial(ListField, Issue)

base_schema = GeoFormSchemaNode(Issue)

base_schema.add_before(
    'type_id',
    colander.SequenceSchema(
        colander.SchemaNode(colander.Int()),
        name='category',
        title='Category',
        widget=RelationSelect2Widget(
            Category,
            'id',
            'label_fr',
            order_by='label_fr'
        )
    )
)


@view_defaults(match_param='table=issues')
class IssueViews(AbstractViews):

    _model = Issue
    _base_schema = base_schema
    _id_field = 'hash'

    _list_fields = [
        _list_field('id'),
        _list_field('request_date'),
        _list_field('description'),
    ]

    @view_config(route_name='c2cgeoform_index',
                 renderer='../templates/index.jinja2')
    def index(self):
        return super().index()

    @view_config(route_name='c2cgeoform_grid',
                 renderer='json')
    def grid(self):
        return super().grid()

    @view_config(route_name='c2cgeoform_item',
                 request_method='GET',
                 renderer='../templates/edit.jinja2')
    def edit(self):
        return super().edit()

    @view_config(route_name='c2cgeoform_item',
                 request_method='DELETE',
                 renderer='json')
    def delete(self):
        return super().delete()

    @view_config(route_name='c2cgeoform_item',
                 request_method='POST',
                 renderer='../templates/edit.jinja2')
    def save(self):
        return super().save()
