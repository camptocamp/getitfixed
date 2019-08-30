from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews

from getitfixed.models.getitfixed import (
    Event,
)

base_schema = GeoFormSchemaNode(Event)


@view_defaults(match_param=('application=admin', 'table=events'))
class EventViews(AbstractViews):

    _model = Event
    _base_schema = base_schema
    _id_field = 'id'

    @view_config(route_name='c2cgeoform_item',
                 request_method='GET',
                 renderer='../../templates/edit.jinja2')
    def edit(self):
        return super().edit()

    @view_config(route_name='c2cgeoform_item',
                 request_method='POST',
                 renderer='../../templates/edit.jinja2')
    def save(self):
        resp = super().save()
        if isinstance(resp, HTTPFound):
            # Update issue status
            # FIXME: Should be placed in a trigger after first migration is created
            self._obj.issue.status = self._obj.status

            # Redirect to issue form
            return HTTPFound(self._request.route_url(
                'c2cgeoform_item',
                table='issues',
                id=self._obj.issue.hash))
        return resp
