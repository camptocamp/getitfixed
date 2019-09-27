from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews

from getitfixed.models.getitfixed import Event, USER_CUSTOMER

from getitfixed.emails.email_service import send_email

base_schema = GeoFormSchemaNode(Event)


@view_defaults(match_param="table=events")
class EventViews(AbstractViews):

    _model = Event
    _base_schema = base_schema
    _id_field = "id"

    @view_config(
        route_name="c2cgeoform_item",
        request_method="GET",
        renderer="../../templates/edit.jinja2",
    )
    def edit(self):
        return super().edit()

    @view_config(
        route_name="c2cgeoform_item",
        request_method="POST",
        renderer="../../templates/edit.jinja2",
    )
    def save(self):
        resp = super().save()
        if isinstance(resp, HTTPFound):
            event_status = self._obj.status
            route = "c2cgeoform_item"
            # send a email when the status has changed
            if event_status != self._obj.issue.status:
                # update issue status
                self._obj.issue.status = event_status

                # send a specific email when the status has been set to resolved
                if event_status == "resolved" and self._obj.user is not True:
                    self.send_notification_email(
                        self._obj.issue.email,
                        "resolved_issue_email",
                        **{
                            "issue": self._obj.issue,
                            "issue-link": self._request.route_url(
                                "c2cgeoform_item", id=self._obj.issue.hash
                            ),
                        }
                    )
                # send email to user when admin has commented
                elif self._obj.private is False and event_status:
                    self.send_notification_email(
                        self._obj.issue.email,
                        "update_issue_email",
                        **{
                            "issue": self._obj.issue,
                            "event": self._obj,
                            "issue-link": self._request.route_url(
                                "c2cgeoform_item", id=self._obj.issue.hash
                            ),
                        }
                    )
            else:
                # send email to admin when user has commented
                if self._obj.author == USER_CUSTOMER:
                    route = "c2cgeoform_item_private"
                    self.send_notification_email(
                        self._obj.issue.email,
                        "update_issue_email",
                        **{
                            "issue": self._obj.issue,
                            "event": self._obj,
                            "issue-link": self._request.route_url(
                                "c2cgeoform_item", id=self._obj.issue.hash
                            ),
                        }
                    )
            # Redirect to issue form
            return HTTPFound(
                self._request.route_url(
                    route,
                    application=self._request.matchdict["application"],
                    table="issues",
                    id=self._obj.issue.hash,
                )
            )
        return resp

    def send_notification_email(self, send_to, template_name, **template_kwargs):
        send_email(
            request=self._request,
            to=send_to,
            template_name=template_name,
            template_kwargs=template_kwargs,
        )
