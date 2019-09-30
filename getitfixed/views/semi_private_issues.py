from functools import partial

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPNotFound
from deform import Button, Form
from deform.widget import HiddenWidget

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.models.getitfixed import USER_ADMIN, USER_CUSTOMER, Event, Issue

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
    _author = USER_CUSTOMER

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
            event.status = issue.status
            event.author = self._author

            event_schema = GeoFormSchemaNode(Event)
            self.get_schema(event_schema, self._hidden_columns)

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
                    "event_form_render_kwargs": {
                        "request": self._request,
                        "user_admin": USER_ADMIN,
                    },
                }
            )
            resp.update({"events": self.get_events(issue)})
            return resp

    @staticmethod
    def get_schema(event_schema, columns):
        for column in columns:
            event_schema.get(column).widget = HiddenWidget()
        return event_schema

    @staticmethod
    def get_events(issue):
        return issue.public_events
