from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

import colander
from deform.widget import HiddenWidget

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews

from getitfixed.models.getitfixed import Event, USER_REPORTER

from getitfixed.emails.email_service import send_email

base_schema = GeoFormSchemaNode(Event)
base_schema["comment"].missing = colander.required
base_schema["status"].widget = HiddenWidget()
base_schema["private"].widget = HiddenWidget()


@view_defaults(match_param=("application=getitfixed_private", "table=events"))
class EventViews(AbstractViews):

    _model = Event
    _base_schema = base_schema
    _id_field = "id"

    @view_config(
        route_name="c2cgeoform_item",
        request_method="POST",
        renderer="getitfixed:templates/admin/events/edit.jinja2",
    )
    def save(self):
        resp = super().save()
        if isinstance(resp, HTTPFound):
            if self._obj.author == USER_REPORTER:
                self.send_notification_email(
                    self._obj.issue.category.email,
                    "update_issue_email",
                    self._request.route_url(
                        "c2cgeoform_item",
                        application="getitfixed_admin",
                        table="issues",
                        id=self._obj.issue.hash,
                        _anchor="existing_events_form",
                    ),
                )
            # Redirect to issue form
            return HTTPFound(
                self._request.route_url(
                    "c2cgeoform_item",
                    table="issues",
                    id=self._obj.issue.hash,
                    _anchor="existing_events_form",
                )
            )
        return resp

    def send_notification_email(self, send_to, template_name, link):
        send_email(
            request=self._request,
            to=send_to,
            template_name=template_name,
            template_kwargs={
                "username": "{} {}".format(
                    self._obj.issue.firstname, self._obj.issue.lastname
                ),
                "issue": self._obj.issue,
                "event": self._obj,
                "issue-link": link,
            },
        )
