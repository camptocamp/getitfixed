from functools import partial

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm import subqueryload

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.models.getitfixed import (
    Issue,
    Type,
)

_list_field = partial(ListField, Issue)

base_schema = GeoFormSchemaNode(Issue)


@view_defaults(match_param=('application=admin', 'table=issues'))
class IssueViews(AbstractViews):

    _model = Issue
    _base_schema = base_schema
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

    def _base_query(self):
        return super()._base_query(). \
            outerjoin(Issue.type). \
            options(subqueryload(Issue.type))

    @view_config(route_name='c2cgeoform_index',
                 renderer='../../templates/index.jinja2')
    def index(self):
        return super().index()

    @view_config(route_name='c2cgeoform_grid',
                 renderer='json')
    def grid(self):
        return super().grid()

    def _grid_actions(self):
        return []

    def _item_actions(self, item):
        return []

    def _form(self, *args, **kwargs):
        form = super()._form(*args, **kwargs)
        for child in form:
            if child.name in (
                'request_date',
                'type_id',
                'description',
                'localisation',
                'geometry',
                'photos',
                'firstname',
                'lastname',
                'phone',
                'email',
            ):
                child.widget.readonly = True
        return form

    @view_config(route_name='c2cgeoform_item',
                 request_method='GET',
                 renderer='../../templates/edit.jinja2')
    def edit(self):
        if self._is_new():
            return HTTPNotFound()
        else:
            return super().edit()

    @view_config(route_name='c2cgeoform_item',
                 request_method='POST',
                 renderer='../../templates/edit.jinja2')
    def save(self):
        return super().save()
