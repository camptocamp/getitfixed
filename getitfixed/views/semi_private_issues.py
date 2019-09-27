from functools import partial

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPNotFound
from deform import Button, Form
from deform.widget import DateTimeInputWidget, HiddenWidget

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.models.getitfixed import STATUS_ADMIN, Event, Issue, Type

from getitfixed.i18n import _


_list_field = partial(ListField, Issue)

base_schema = GeoFormSchemaNode(
    Issue,
    excludes=[
        "email",
        "firstname",
        "lastname",
        "phone",
        "photos",
        "events",
        "public_events",
    ],
)


@view_defaults(match_param="table=issues")
class IssueViews(AbstractViews):
    _model = Issue
    _base_schema = base_schema
    _id_field = "hash"
    _hidden_columns = ["status", "private"]

    @view_config(
        route_name="c2cgeoform_item_private",
        request_method="GET",
        renderer="../templates/admin/issue/edit.jinja2",
    )
    def edit(self):
        if self._is_new():
            return HTTPNotFound()
        else:
            # Create a readonly issue form
            resp = super().edit(readonly=True)

            issue = self._get_object()

            event = Event(issue_id=issue.id)
            self.set_event_columns(event, issue)

            event_schema = GeoFormSchemaNode(Event)
            self.hide_schema_nodes(event_schema, self._hidden_columns)

            event_form = Form(
                event_schema,
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
            resp.update({"events": self.get_events_to_display(issue)})
            return resp

    @staticmethod
    def set_event_columns(event, issue):
        event.status = STATUS_ADMIN
        event.private = False
        return event

    @staticmethod
    def hide_schema_nodes(event_schema, columns):
        for column in columns:
            event_schema.get(column).widget = HiddenWidget()
        return event_schema

    @staticmethod
    def get_events_to_display(issue):
        return issue.public_events
