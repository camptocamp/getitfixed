from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.threadlocal import get_current_request
from functools import partial

from sqlalchemy.orm import subqueryload

from colander import SchemaNode, Int
from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.ext.deform_ext import RelationSelectWidget
from c2cgeoform.views.abstract_views import AbstractViews, ListField

from getitfixed.models.getitfixed import Category, Issue, Type, STATUS_NEW
from getitfixed.emails.email_service import send_email

from getitfixed.i18n import _

_list_field = partial(ListField, Issue)

new_schema = GeoFormSchemaNode(Issue, excludes=["request_date", "events", "status"])

new_schema.add_before(
    "type_id",
    SchemaNode(
        Int(),
        name="category_id",
        title=_("Category"),
        widget=RelationSelectWidget(Category, "id", "label_fr", order_by="label_fr"),
    ),
)

follow_schema = GeoFormSchemaNode(
    Issue,
    includes=[
        "status",
        "request_date",
        "type_id",
        "description",
        "localisation",
        "geometry",
    ],
)


def get_types(request):
    return {
        "fields": ["category_id", "type_id"],
        "values": [
            dict(id=o.id, cat=o.category_id, label=o.label_fr)
            for o in request.dbsession.query(Type)
        ],
    }


def get_issue_url(issue):
    # Request isn't available here without breaking changes in c2cgeoform
    # use of get_current_request should be safe here, cf
    # https://docs.pylonsproject.org/projects/pyramid/en/latest/api/threadlocal.html
    request = get_current_request()
    return request.route_url("c2cgeoform_item", id=issue.id)


@view_defaults(match_param=("application=getitfixed", "table=issues"))
class IssueViews(AbstractViews):

    _model = Issue
    _base_schema = new_schema
    _id_field = "id"
    _geometry_field = "geometry"

    _list_fields = [
        _list_field("id", key="url", renderer=get_issue_url),
        _list_field(
            "type", key="category", renderer=lambda issue: issue.type.category.label_fr
        ),
        _list_field("type", renderer=lambda issue: issue.type.label_fr),
        _list_field(
            "type",
            key="icon",
            renderer=lambda issue: partial(
                issue.icon_url, request=get_current_request()
            )(),
        ),
    ]

    def _base_query(self):
        return (
            super()
            ._base_query()
            .outerjoin(Issue.type)
            .filter(Issue.status.notin_([STATUS_NEW]))
            .filter(Issue.private.is_(False))
            .options(subqueryload(Issue.type))
        )

    @view_config(
        route_name="c2cgeoform_index",
        renderer="getitfixed:templates/public/issues/index.jinja2",
    )
    def map(self):
        return super().map(self._request.registry.settings["getitfixed"].get("map", {}))

    @view_config(route_name="c2cgeoform_geojson", renderer="json", request_method="GET")
    def geojson(self):
        return super().geojson()

    def _grid_actions(self):
        return []

    def _grid_item_actions(self, item):
        return {"dropdown": []}

    def _get_object(self):
        obj = super()._get_object()
        if obj.status == STATUS_NEW or obj.private:
            raise HTTPNotFound()
        return obj

    @view_config(
        route_name="c2cgeoform_item",
        request_method="GET",
        renderer="getitfixed:templates/public/issues/edit.jinja2",
    )
    def edit(self):
        if self._is_new():
            base_edit = super().edit()
            base_edit["form_render_kwargs"].update({"deps": get_types(self._request)})
            base_edit["item_name"] = _("New")
            base_edit["new"] = True
            return base_edit
        else:
            if not self._request.matchdict["id"].isdigit():
                raise HTTPNotFound()
            base_edit = super().edit(schema=follow_schema, readonly=True)
            obj = self._get_object()
            base_edit["item_name"] = obj.description
            base_edit["new"] = False
            base_edit["wms_layer"] = obj.type.wms_layer
            return base_edit

    # For development/testing purpose
    @view_config(
        route_name="c2cgeoform_item_duplicate",
        request_method="GET",
        renderer="getitfixed:templates/public/issues/edit.jinja2",
    )
    def duplicate(self):
        base_duplicate = super().duplicate()
        base_duplicate["form_render_kwargs"].update({"deps": get_types(self._request)})
        base_duplicate["item_name"] = _("New")
        return base_duplicate

    @view_config(
        route_name="c2cgeoform_item",
        request_method="POST",
        renderer="getitfixed:templates/public/issues/edit.jinja2",
    )
    def save(self):
        resp = super().save()
        if self._is_new():

            if isinstance(resp, HTTPFound):
                # Send email to the issue Reporter
                self.send_notification_email(
                    self._obj.email,
                    "new_issue_email",
                    self._request.route_url(
                        "c2cgeoform_item",
                        application="getitfixed_private",
                        id=self._obj.hash,
                    ),
                )
                # Send email to the category Manager
                self.send_notification_email(
                    self._obj.category.email,
                    "admin_new_issue_email",
                    self._request.route_url(
                        "c2cgeoform_item",
                        application="getitfixed_admin",
                        id=self._obj.hash,
                    ),
                )
                return HTTPFound(
                    self._request.route_url(
                        "c2cgeoform_item",
                        application="getitfixed_private",
                        id=self._obj.hash,
                        _query=[("msg_col", "submit_ok")],
                    )
                )

        resp.update({"item_name": _("New"), "new": self._is_new()})
        return resp

    def send_notification_email(self, send_to, template_name, link):
        send_email(
            request=self._request,
            to=send_to,
            template_name=template_name,
            template_kwargs={
                "username": "{} {}".format(self._obj.firstname, self._obj.lastname),
                "issue": self._obj,
                "issue-link": link,
            },
        )
