from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import AbstractViews

from getitfixed.models.getitfixed import Event

from getitfixed.emails.email_service import send_email

base_schema = GeoFormSchemaNode(Event)


@view_defaults(match_param=("application=admin", "table=events"))
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
            # Update issue status
            # FIXME: Should be placed in a trigger after first migration is created
            event_status = self._obj.status
            # send a email when the status has changed
            if event_status != self._obj.issue.status:
                # send a specific email when the status has been set to resolved
                if event_status == "resolved":
                    send_email(
                        request=self._request,
                        to=self._obj.issue.email,
                        template_name="resolved_issue_email",
                        template_kwargs={"issue": self._obj.issue},
                    )
                else:
                    send_email(
                        request=self._request,
                        to=self._obj.issue.email,
                        template_name="update_issue_email",
                        template_kwargs={"issue": self._obj.issue, "event": self._obj},
                    )
            self._obj.issue.status = event_status

            # Redirect to issue form
            return HTTPFound(
                self._request.route_url(
                    "c2cgeoform_item", table="issues", id=self._obj.issue.hash
                )
            )
        return resp
