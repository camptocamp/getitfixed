from functools import partial

from pyramid.view import view_config, view_defaults

from sqlalchemy.orm import subqueryload

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import ListField

from getitfixed.models.getitfixed import (
    Event,
    Issue,
    Type,
    USER_ADMIN,
    STATUS_IN_PROGRESS,
    STATUS_REPORTER,
    STATUS_NEW,
)
from getitfixed.views.private.semi_private_issues import IssueViews

_list_field = partial(ListField, Issue)

base_schema = GeoFormSchemaNode(Issue, excludes=["events", "public_events"])
route = "c2cgeoform_item"
event_schema = GeoFormSchemaNode(Event)


@view_defaults(match_param=("application=admin", "table=issues"))
class IssueAdminViews(IssueViews):

    _author = USER_ADMIN
    _event_schema = event_schema
    _application = "admin"

    _list_fields = [
        _list_field("id"),
        _list_field("status"),
        _list_field("request_date"),
        _list_field(
            "type_id",
            renderer=lambda issue: issue.type.label_fr,
            sort_column=Type.label_fr,
            filter_column=Type.label_fr,
        ),
        _list_field("description"),
        _list_field("localisation"),
        _list_field("firstname"),
        _list_field("lastname"),
        _list_field("phone"),
        _list_field("email"),
    ]
    _list_ordered_field = [Issue.request_date.desc()]

    def _base_query(self):
        query = (
            super()
            ._base_query()
            .outerjoin(Issue.type)
            .options(subqueryload(Issue.type))
        )
        # return all issues that are not closed
        if not self._request.GET.get("all"):
            query = query.filter(
                Issue.status.in_([STATUS_IN_PROGRESS, STATUS_REPORTER, STATUS_NEW])
            )
        return query

    @view_config(
        route_name="c2cgeoform_index", renderer="../../templates/admin/index.jinja2"
    )
    def index(self):
        return super().index()

    @view_config(route_name="c2cgeoform_grid", renderer="json")
    def grid(self):
        return super().grid()

    def _grid_actions(self):
        return []

    def _item_actions(self, item):
        return []

    @view_config(
        route_name="c2cgeoform_item",
        request_method="GET",
        renderer="../../templates/admin/issue/edit.jinja2",
    )
    def edit(self):
        return super().edit()

    @staticmethod
    def events(issue):
        return issue.events

    @view_config(
        route_name="c2cgeoform_item",
        request_method="POST",
        renderer="../../templates/edit.jinja2",
    )
    def save(self):
        return super().save()
