from functools import partial

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm import subqueryload

from deform import Button, Form
from deform.widget import DateTimeInputWidget

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.i18n import _
from getitfixed.models.getitfixed import Event, Issue, Type

_list_field = partial(ListField, Issue)

base_schema = GeoFormSchemaNode(Issue, excludes=["events"])
events_schema = GeoFormSchemaNode(Issue, includes=["events"])


@view_defaults(match_param=("application=admin", "table=issues"))
class IssueViews(AbstractViews):

    _model = Issue
    _base_schema = base_schema
    _id_field = "hash"

    _list_fields = [
        _list_field("id"),
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
        _list_field("status"),
    ]

    def _base_query(self):
        return (
            super()
            ._base_query()
            .outerjoin(Issue.type)
            .options(subqueryload(Issue.type))
        )

    @view_config(route_name="c2cgeoform_index", renderer="../../templates/index.jinja2")
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
        if self._is_new():
            return HTTPNotFound()
        else:
            # Create a readonly issue form
            resp = super().edit(readonly=True)

            issue = self._get_object()

            # Create a new event form
            event = Event(issue_id=issue.id)
            event.status = issue.status

            events = events_schema.get("events").children
            for e in events:
                e.get("date").widget = DateTimeInputWidget()

            event_form = Form(
                GeoFormSchemaNode(Event),
                formid="new_event_form",
                buttons=[Button(name="formsubmit", title=_("Submit"))],
                action=self._request.route_url(
                    "c2cgeoform_item", table="events", id="new"
                ),
            )
            resp.update(
                {
                    "event_form": event_form,
                    "event_form_render_args": (event_form.schema.dictify(event),),
                    "event_form_render_kwargs": {"request": self._request},
                }
            )

            # Create an issue form with only existing events property
            events_form = Form(events_schema, formid="existing_events_form")
            resp.update(
                {
                    "events_form": events_form,
                    "events_form_render_args": (events_schema.dictify(issue),),
                    "events_form_render_kwargs": {
                        "request": self._request,
                        "readonly": True,
                    },
                }
            )

            return resp

    @view_config(
        route_name="c2cgeoform_item",
        request_method="POST",
        renderer="../../templates/edit.jinja2",
    )
    def save(self):
        return super().save()
