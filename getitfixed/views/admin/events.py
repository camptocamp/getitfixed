from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews

from getitfixed.models.getitfixed import Event

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

            # send a email when the status has changed
            if event_status != self._obj.issue.status:
                # Update issue status
                # FIXME: Should be placed in a trigger after first migration is created
                self._obj.issue.status = event_status
                # Do not send comment en email if it is private
                self._obj.comment = "" if self._obj.private else self._obj.comment

                # send a specific email when the status has been set to resolved
                if event_status == "resolved":
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
                elif event_status == "waiting_for_admin":
                    self.send_notification_email(
                        self._obj.issue.category.email,
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

            # Update issue status
            # FIXME: Should be placed in a trigger after first migration is created
            self._obj.issue.status = self._obj.status
            # For the semi private view
            if self._obj.status == "waiting_for_admin":
                route = "c2cgeoform_item_private"
            else:
                route = "c2cgeoform_item"
            self._obj.issue.status = self._obj.status
            # Redirect to issue form
            return HTTPFound(
                self._request.route_url(route, table="issues", id=self._obj.issue.hash)
            )
        return resp

    def send_notification_email(self, send_to, template_name, **template_kwargs):
        send_email(
            request=self._request,
            to=send_to,
            template_name=template_name,
            template_kwargs=template_kwargs,
        )
