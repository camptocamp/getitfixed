from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.threadlocal import get_current_request
from functools import partial
from geojson import FeatureCollection, Feature

from sqlalchemy.orm import subqueryload
from sqlalchemy import JSON

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
        title="Category",
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


def get_issue_link(issue):
    # Request isn't available here without breaking changes in c2cgeoform
    # use of get_current_request should be safe here, cf
    # https://docs.pylonsproject.org/projects/pyramid/en/latest/api/threadlocal.html
    request = get_current_request()
    if request is None:
        return issue.description
    uri = request.route_url("c2cgeoform_item", id=issue.id)
    return '<a href="{}">{}</a>'.format(uri, issue.description)


@view_defaults(match_param=("application=getitfixed", "table=issues"))
class IssueViews(AbstractViews):

    _model = Issue
    _base_schema = new_schema
    _id_field = "id"

    _list_fields = [
        # _list_field('id'),
        _list_field("description", renderer=get_issue_link),
        _list_field(
            "type_id",
            renderer=lambda issue: issue.type.label_fr,
            sort_column=Type.label_fr,
            filter_column=Type.label_fr,
        ),
        _list_field("localisation"),
        _list_field(
            "request_date",
            renderer=lambda issue: issue.request_date.strftime("%d/%m/%Y"),
        ),
        # _list_field('firstname'),
        # _list_field('lastname'),
        # _list_field('phone'),
        # _list_field('email'),
    ]

    MSG_COL = {
        "submit_ok": _(
            "Thank you for your report, "
            "it has been registered with following details, "
            "and will be treated as soon as possible."
        ),
        "copy_ok": _("Please check that the copy fits before submitting."),
    }

    def _base_query(self):
        return (
            super()
            ._base_query()
            .outerjoin(Issue.type)
            .filter(Issue.status.notin_([STATUS_NEW]))
            .options(subqueryload(Issue.type))
        )

    @view_config(
        route_name="c2cgeoform_index",
        renderer="getitfixed:templates/public/issues/index.jinja2",
    )
    def index(self):
        return super().index()

    @view_config(route_name="c2cgeoform_grid", renderer="json")
    def grid(self):
        return super().grid()

    @view_config(route_name="issues_geojson", renderer="json", request_method="GET")
    def geojson(self):
        query = (
            self._request.dbsession.query(
                Issue.id,
                Issue.geometry.ST_Transform(3857).ST_AsGeoJSON().cast(JSON),
                Type,
            )
            .join(Type)
            .join(Category, Type.category_id == Category.id)
        )

        features = list()
        for id, geom, type in query.all():
            url = self._request.route_url(
                "c2cgeoform_item", application="getitfixed", id=id
            )
            features.append(
                Feature(
                    geometry=geom,
                    properties={
                        "url": url,
                        "category": type.category.label_fr,
                        "type": type.label_fr,
                        "icon": self._request.static_url(
                            "getitfixed:static/assets/{}".format(type.category.icon)
                        ),
                    },
                )
            )
        return FeatureCollection(features)

    def _grid_actions(self):
        return []

    def _grid_item_actions(self, item):
        return {"dropdown": []}

    def _item_actions(self, item):
        return []

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
            return base_edit
        else:
            base_edit = super().edit(schema=follow_schema, readonly=True)
            base_edit["item_name"] = self._get_object().description
            base_edit["form_render_kwargs"].update(
                {
                    "category_icon": self._request.static_url(
                        "getitfixed:static/assets/{}".format(
                            self._get_object().category.icon
                        )
                    )
                }
            )
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
        base_save = super().save()
        if self._is_new():

            if isinstance(base_save, HTTPFound):
                # Send email to the issue Reporter
                self.send_notification_email(
                    "new_issue_email",
                    **{
                        "username": "{} {}".format(
                            self._obj.firstname, self._obj.lastname
                        ),
                        "issue": self._obj,
                        "issue-link": self._request.route_url(
                            "c2cgeoform_item_private", id=self._obj.hash
                        ),
                    },
                )
                # Send email to the category Manager
                self.send_notification_email(
                    "admin_new_issue_email",
                    **{
                        "username": "",
                        "issue": self._obj,
                        "issue-link": self._request.route_url(
                            "c2cgeoform_item", application="admin", id=self._obj.hash
                        ),
                    },
                )
            else:
                base_save["item_name"] = _("New")
        return base_save

    def send_notification_email(self, template_name, **template_kwargs):
        send_email(
            request=self._request,
            to=self._obj.email,
            template_name=template_name,
            template_kwargs=template_kwargs,
        )
