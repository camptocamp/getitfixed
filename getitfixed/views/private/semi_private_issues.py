from functools import partial

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPNotFound
from deform import Button, Form
from deform.widget import HiddenWidget

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.models.getitfixed import USER_ADMIN, USER_REPORTER, Event, Issue

from getitfixed.i18n import _


_list_field = partial(ListField, Issue)

base_schema = GeoFormSchemaNode(
    Issue,
    excludes=["email", "firstname", "lastname", "phone", "events", "public_events"],
)
event_schema = GeoFormSchemaNode(Event)
event_schema["status"].widget = HiddenWidget()
event_schema["private"].widget = HiddenWidget()


@view_defaults(match_param="table=issues")
class IssueViews(AbstractViews):
    _model = Issue
    _base_schema = base_schema
    _id_field = "hash"
    _author = USER_REPORTER
    _event_schema = event_schema
    _application = "getitfixed"

    MSG_COL = {
        "submit_ok": _(
            "Thank you for your report, "
            "it has been registered with following details, "
            "and will be treated as soon as possible."
        ),
        "copy_ok": _("Please check that the copy fits before submitting."),
    }

    @view_config(
        route_name="c2cgeoform_item_private",
        request_method="GET",
        renderer="getitfixed:templates/admin/issues/edit.jinja2",
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
            event_form = Form(
                self._event_schema,
                formid="new_event_form",
                buttons=[Button(name="formsubmit", title=_("Submit"))],
                action=self._request.route_url(
                    "c2cgeoform_item",
                    application=self._application,
                    table="events",
                    id="new",
                ),
            )
            resp.update(
                {
                    "event_form": event_form,
                    "event_form_render_args": (event_form.schema.dictify(event),),
                    "event_form_render_kwargs": {
                        "request": self._request,
                        "user_admin": USER_ADMIN,
                        "obj": issue,
                    },
                    "events": self.events(issue),
                    "wms_layer": self._get_object().type.wms_layer,
                }
            )
            return resp

    @staticmethod
    def events(issue):
        return issue.public_events
