from pyramid.view import view_config
from pyramid.view import view_defaults
from functools import partial

from sqlalchemy.orm import subqueryload

import colander
from c2cgeoform.schema import (
    GeoFormSchemaNode,
    GeoFormManyToManySchemaNode,
    manytomany_validator,
)
from c2cgeoform.ext.deform_ext import RelationCheckBoxListWidget
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from ..models.c2cgeoform_demo import Excavation, Situation

_list_field = partial(ListField, Excavation)

base_schema = GeoFormSchemaNode(Excavation)
base_schema.add_before(
    'contact_persons',
    colander.SequenceSchema(
        GeoFormManyToManySchemaNode(Situation),
        name='situations',
        title='Situations',
        widget=RelationCheckBoxListWidget(
            Situation,
            'id',
            'name',
            order_by='name'
        ),
        validator=manytomany_validator
    )
)
base_schema.add_unique_validator(Excavation.reference_number, Excavation.hash)


@view_defaults(match_param='table=excavations')
class ExcavationViews(AbstractViews):

    _model = Excavation
    _base_schema = base_schema
    _id_field = 'hash'

    _list_fields = [
        _list_field('reference_number'),
        _list_field('request_date'),
        _list_field('description'),
        _list_field('location_town'),
        _list_field('responsible_company'),
        _list_field('situations',
                    renderer=lambda excavation: ", ".join(
                        [s.name for s in excavation.situations]),
                    filter_column=Situation.name)
    ]

    def _base_query(self):
        return super()._base_query().distinct(). \
            outerjoin('situations'). \
            options(subqueryload('situations'))

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

    @view_config(route_name='c2cgeoform_item_duplicate',
                 request_method='GET',
                 renderer='../templates/edit.jinja2')
    def duplicate(self):
        return super().duplicate()

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
