from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews

from getitfixed.models.getitfixed import Event, USER_ADMIN

from getitfixed.emails.email_service import send_email

base_schema = GeoFormSchemaNode(Event)


@view_defaults(
    match_param=("application=getitfixed_admin", "table=events"),
    permission="getitfixed_admin",
)
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
            event_status = self._obj.status
            route = "c2cgeoform_item"
            # update issue status
            self._obj.issue.status = event_status

            # send a specific email to user when the status has been set to resolved
            if event_status != self._obj.issue.status and event_status == "resolved":
                self.send_notification_email(
                    self._obj.issue.email,
                    "resolved_issue_email",
                    self._request.route_url(
                        "c2cgeoform_item", table="issues", id=self._obj.issue.hash
                    ),
                )
            # send email to user when admin has commented and message is not private
            elif (
                self._obj.private is False
                and event_status
                and self._obj.author == USER_ADMIN
            ):
                self.send_notification_email(
                    self._obj.issue.email,
                    "update_issue_email",
                    self._request.route_url(
                        "c2cgeoform_item_private",
                        application="getitfixed",
                        table="issues",
                        id=self._obj.issue.hash,
                        _anchor="existing_events_form",
                    ),
                )
            # Redirect to issue form
            return HTTPFound(
                self._request.route_url(
                    route,
                    application=self._request.matchdict["application"],
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
