from functools import partial

from pyramid.view import view_config, view_defaults
from sqlalchemy.orm import subqueryload

from c2cgeoform.schema import GeoFormSchemaNode
from c2cgeoform.views.abstract_views import ItemAction, ListField

from getitfixed.i18n import _
from getitfixed.models.getitfixed import (
    Event,
    Category,
    Issue,
    Type,
    USER_ADMIN,
    STATUS_RESOLVED,
)
from getitfixed.views.private.issues import IssueViews

_list_field = partial(ListField, Issue)

route = "c2cgeoform_item"
event_schema = GeoFormSchemaNode(Event)

base_schema = GeoFormSchemaNode(
    Issue,
    includes=[
        "id",
        "status",
        "request_date",
        "type_id",
        "description",
        "localisation",
        "geometry",
        "photos",
        "firstname",
        "lastname",
        "phone",
        "email",
        "private",
    ],
    overrides={"private": {"exclude": False}},
)

MAX_DESCR_LEN = 40


@view_defaults(
    match_param=("application=getitfixed_admin", "table=issues"),
    permission="getitfixed_admin",
)
class IssueAdminViews(IssueViews):

    _author = USER_ADMIN
    _event_schema = event_schema
    _base_schema = base_schema
    _application = "getitfixed_admin"

    _list_fields = [
        _list_field("id"),
        _list_field("status"),
        _list_field("request_date"),
        _list_field(
            "type_id",
            renderer=lambda issue: issue.type.label_fr,
            sort_column=Type.label_fr,
            filter_column=Type.label_fr,
        ),
        _list_field(
            "description",
            renderer=lambda issue: (issue.description[:MAX_DESCR_LEN] + "…")
            if len(issue.description) > MAX_DESCR_LEN
            else issue.description,
        ),
        _list_field("localisation"),
        _list_field("firstname"),
        _list_field("lastname"),
        _list_field("phone"),
        _list_field("email"),
    ]
    _list_ordered_fields = [Issue.request_date.desc()]

    def _base_query(self):
        query = (
            super()
            ._base_query()
            .outerjoin(Issue.type)
            .options(subqueryload(Issue.type))
        )

        status = self._request.params.get("status", "open")
        if status == "open":
            # return all issues that are not closed
            query = query.filter(Issue.status != STATUS_RESOLVED)

        # filter issues based on category id
        category = int(self._request.params.get("category", 0))
        if category != 0:  # 0 is for all issues
            query = query.filter(Issue.category.has(id=category))
        return query

    @view_config(
        route_name="c2cgeoform_index",
        renderer="getitfixed:templates/admin/issues/index.jinja2",
    )
    def index(self):
        resp = super().index()
        cats = self._request.dbsession.query(Category).all()

        label = (
            "label_fr" if self._request.localizer.locale_name == "fr" else "label_en"
        )
        resp.update(
            {
                "categories": list(
                    map(lambda c: {"id": c.id, "value": getattr(c, label)}, cats)
                )
            }
        )
        return resp

    @view_config(route_name="c2cgeoform_grid", renderer="json")
    def grid(self):
        return super().grid()

    def _grid_actions(self):
        return []

    def _item_actions(self, item, readonly=False):
        actions = []
        if item.private:
            actions.append(
                ItemAction(
                    name="set_private",
                    label=_("Make this issue public"),
                    icon="glyphicon glyphicon-lock",
                    url=self._request.route_url(
                        "getitfixed_set_public", id=getattr(item, self._id_field)
                    ),
                    method="POST",
                )
            )
        else:
            actions.append(
                ItemAction(
                    name="set_private",
                    label=_("Make this issue private"),
                    icon="glyphicon glyphicon-lock",
                    url=self._request.route_url(
                        "getitfixed_set_private", id=getattr(item, self._id_field)
                    ),
                    method="POST",
                )
            )
        return actions

    @view_config(
        route_name="c2cgeoform_item",
        request_method="GET",
        renderer="getitfixed:templates/admin/issues/edit.jinja2",
    )
    def edit(self):
        return super().edit()

    @staticmethod
    def events(issue):
        return issue.events

    @view_config(
        route_name="c2cgeoform_item",
        request_method="POST",
        renderer="getitfixed:templates/admin/issues/edit.jinja2",
    )
    def save(self):
        return super().save()

    @view_config(
        route_name="getitfixed_set_private", request_method="POST", renderer="json"
    )
    def set_private(self):
        obj = self._get_object()
        obj.private = True
        return {
            "success": True,
            "redirect": self._request.route_url(
                "c2cgeoform_item",
                id=getattr(obj, self._id_field),
                _query=[("msg_col", "submit_ok")],
            ),
        }

    @view_config(
        route_name="getitfixed_set_public", request_method="POST", renderer="json"
    )
    def set_public(self):
        obj = self._get_object()
        obj.private = False
        return {
            "success": True,
            "redirect": self._request.route_url(
                "c2cgeoform_item",
                id=getattr(obj, self._id_field),
                _query=[("msg_col", "submit_ok")],
            ),
        }
