# coding=utf-8
from uuid import uuid4
from pkg_resources import resource_filename

from pyramid.i18n import make_localizer

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Integer,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.associationproxy import association_proxy

import geoalchemy2
from xml.sax.saxutils import quoteattr

import colander
from deform.widget import (
    CheckboxWidget,
    FormWidget,
    HiddenWidget,
    SelectWidget,
    SequenceWidget,
    TextAreaWidget,
    TextInputWidget,
)
from c2c.template.config import config

from c2cgeoform import default_map_settings
from c2cgeoform.ext.deform_ext import RelationSelectWidget
from c2cgeoform.ext import colander_ext, deform_ext
from c2cgeoform.models import FileData

from getitfixed.i18n import _
from getitfixed.models.meta import Base
from getitfixed.url import generate_url

schema = "getitfixed"

_getitfixed_config = (config.get_config() or {}).get("getitfixed", {})
_map_config = {
    **default_map_settings,
    **{"mobile": True},
    **_getitfixed_config.get("map", {}),
}

STATUS_NEW = "new"
STATUS_VALIDATED = "validated"
STATUS_IN_PROGRESS = "in_progress"
STATUS_REPORTER = "waiting_for_reporter"
STATUS_RESOLVED = "resolved"

STATUSES = {
    STATUS_NEW: _("New"),
    STATUS_VALIDATED: _("Validated"),
    STATUS_IN_PROGRESS: _("In progress"),
    STATUS_REPORTER: _("Waiting for Reporter"),
    STATUS_RESOLVED: _("Resolved"),
}

USER_ADMIN = "admin"
USER_REPORTER = "customer"
USER_AUTHORS = {USER_REPORTER: _("Reporter"), USER_ADMIN: _("Administrator")}


def default_icon():
    return _getitfixed_config.get(
        "default_icon", "static://getitfixed:static/icons/cat-default.png"
    )


def default_icon_url(request):
    return generate_url(request, default_icon())


class TelWidget(TextInputWidget):
    def serialize(self, field, cstruct=None, readonly=False, **kw):
        if cstruct is colander.null:
            cstruct = u""
        quoted = quoteattr(cstruct)
        if readonly:
            return cstruct
        return u'<input type="tel" name="%s" pattern="(\\d| )+" value=%s>' % (
            field.name,
            quoted,
        )


class Photo(FileData, Base):
    __tablename__ = "photo"
    __table_args__ = {"schema": schema}
    # Setting unknown to 'preserve' is required in classes used as a
    # FileUpload field.
    __colanderalchemy_config__ = {
        "title": _("Photo"),
        "unknown": "preserve",
        "missing": colander.required,
        "widget": deform_ext.FileUploadWidget(
            get_url=lambda request, id: request.route_url(
                "c2cgeoform_item", table="photos", id=id
            )
        ),
    }
    issue_id = Column(Integer, ForeignKey("{}.issue.id".format(schema)))


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {"schema": schema}
    __colanderalchemy_config__ = {"title": _("Category"), "plural": _("Categories")}

    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"title": _("Identifier"), "widget": HiddenWidget()}},
    )
    label_fr = Column(
        String(50),
        info={
            "colanderalchemy": {"title": _("Label(fr)"), "widget": TextInputWidget()}
        },
    )
    label_en = Column(
        String(50),
        info={
            "colanderalchemy": {"title": _("Label(en)"), "widget": TextInputWidget()}
        },
    )
    email = Column(
        String(50),
        nullable=False,
        info={"colanderalchemy": {"title": _("Email"), "widget": TextInputWidget()}},
    )

    icon = Column(
        String(150),
        info={"colanderalchemy": {"title": _("Label(en)"), "widget": HiddenWidget()}},
    )

    def icon_url(self, request):
        return generate_url(request, self.icon or default_icon())

    def label(self, locale):
        return getattr(self, "label_{}".format(locale))


class Type(Base):
    __tablename__ = "type"
    __table_args__ = {"schema": schema}
    __colanderalchemy_config__ = {"title": _("Type"), "plural": _("Types")}

    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"title": _("Identifier"), "widget": HiddenWidget()}},
    )
    label_fr = Column(
        String(50),
        info={
            "colanderalchemy": {"title": _("Label(fr)"), "widget": TextInputWidget()}
        },
    )
    label_en = Column(
        String(50),
        info={
            "colanderalchemy": {"title": _("Label(en)"), "widget": TextInputWidget()}
        },
    )
    category_id = Column(
        Integer,
        ForeignKey("{}.category.id".format(schema)),
        info={
            "colanderalchemy": {
                "title": _("Category"),
                "widget": RelationSelectWidget(
                    Category,
                    "id",
                    "label_fr",
                    order_by="label_fr",
                    default_value=("", _("- Select -")),
                ),
            }
        },
    )
    category = relationship(Category, backref="types")
    wms_layer = Column(
        String(255),
        info={
            "colanderalchemy": {
                "title": _("WMS layer"),
                "description": _(
                    "Example: https://service.wms/?service=WMS&version=1.0.3&layer=layername"
                ),
                "widget": TextInputWidget(),
            }
        },
    )

    def icon_url(self, request):
        return self.category.icon_url(request)

    def label(self, locale):
        return getattr(self, "label_{}".format(locale))


class Issue(Base):
    __tablename__ = "issue"
    __table_args__ = {"schema": schema}
    __colanderalchemy_config__ = {
        "title": _("Issue"),
        "plural": _("Issues"),
        "widget": FormWidget(fields_template="issue_fields"),
    }

    id = Column(
        Integer,
        primary_key=True,
        info={
            # the `colanderalchemy` property allows to set a custom title for the
            # column or to use a specific widget.
            "colanderalchemy": {"title": _("Identifier"), "widget": HiddenWidget()}
        },
    )
    hash = Column(
        Text,
        nullable=False,
        unique=True,
        default=lambda: str(uuid4()),
        info={"colanderalchemy": {"exclude": True}, "c2cgeoform": {"duplicate": False}},
    )
    request_date = Column(
        Date,
        nullable=False,
        server_default=func.now(),
        info={"colanderalchemy": {"title": _("Request date")}},
    )
    geometry = Column(
        geoalchemy2.Geometry("POINT", 4326, management=True),
        info={
            "colanderalchemy": {
                "title": _("Position"),
                "typ": colander_ext.Geometry(
                    "POINT", srid=4326, map_srid=_map_config["srid"]
                ),
                "widget": deform_ext.MapWidget(
                    map_options=_map_config, item_css_class="item-geometry"
                ),
            }
        },
    )
    type_id = Column(
        Integer,
        ForeignKey("{}.type.id".format(schema)),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": _("Type"),
                "widget": RelationSelectWidget(
                    Type,
                    "id",
                    "label_en",
                    order_by="label_en",
                    default_value=("", _("- Select -")),
                ),
            }
        },
    )
    type = relationship(Type, info={"colanderalchemy": {"exclude": True}})
    status = Column(
        Enum(*tuple(STATUSES.keys()), native_enum=False, name="status"),
        nullable=False,
        default="new",
        info={
            "colanderalchemy": {
                "title": _("Status"),
                "widget": SelectWidget(
                    values=STATUSES.items(), readonly=True, item_css_class="item-status"
                ),
            }
        },
    )

    @property
    def status_de(self):
        return self.status_i18n("de")

    @property
    def status_en(self):
        return self.status_i18n("en")

    @property
    def status_fr(self):
        return self.status_i18n("fr")

    def status_i18n(self, locale):
        localizer = make_localizer(locale, [resource_filename("getitfixed", "locale")])
        return localizer.translate(STATUSES[self.status])

    description = Column(
        Text,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": _("Description of the problem"),
                "widget": TextAreaWidget(rows=3),
            }
        },
    )
    localisation = Column(
        String(254),
        nullable=False,
        info={"colanderalchemy": {"title": _("Localisation")}},
    )
    photos = relationship(
        Photo,
        cascade="all, delete-orphan",
        info={"colanderalchemy": {"title": _("Photos")}},
    )
    firstname = Column(
        String(100), nullable=False, info={"colanderalchemy": {"title": _("Firstname")}}
    )
    lastname = Column(
        String(100), nullable=False, info={"colanderalchemy": {"title": _("Lastname")}}
    )
    phone = Column(
        String(20),
        nullable=False,
        info={"colanderalchemy": {"title": _("Phone"), "widget": TelWidget()}},
    )
    email = Column(
        String(100),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": _("Email"),
                "validator": colander.Email(),
                "description": _(
                    "This field is required to keep you informed about issue events"
                ),
            }
        },
    )
    private = Column(
        Boolean,
        nullable=False,
        server_default=text("False"),
        info={"colanderalchemy": {"title": _("Private"), "exclude": True}},
    )
    events = relationship(
        "Event",
        order_by="desc(Event.date)",
        backref=backref("issue", info={"colanderalchemy": {"exclude": True}}),
        info={
            "colanderalchemy": {
                "title": _("Events"),
                "widget": SequenceWidget(readonly=True, item_css_class="item-events"),
            }
        },
    )
    public_events = relationship(
        "Event",
        order_by="desc(Event.date)",
        primaryjoin="and_(Event.issue_id==Issue.id, Event.private==False)",
    )

    category = association_proxy("type", "category")

    def icon_url(self, request):
        return self.type.icon_url(request) if self.type else default_icon_url(request)


class Event(Base):
    __tablename__ = "event"
    __table_args__ = {"schema": schema}
    __colanderalchemy_config__ = {"title": _("Event"), "plural": _("Events")}
    id = Column(
        Integer,
        primary_key=True,
        info={"colanderalchemy": {"title": _("Identifier"), "widget": HiddenWidget()}},
    )
    issue_id = Column(
        Integer,
        ForeignKey("{}.issue.id".format(schema)),
        nullable=False,
        info={"colanderalchemy": {"title": _("Type"), "widget": HiddenWidget()}},
    )
    status = Column(
        Enum(*tuple(STATUSES.keys()), native_enum=False, name="status"),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": _("Status"),
                "widget": SelectWidget(
                    values=STATUSES.items(), item_css_class="item-status"
                ),
            }
        },
    )
    date = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        info={"colanderalchemy": {"title": _("Date"), "widget": HiddenWidget()}},
    )
    comment = Column(
        Text, info={"colanderalchemy": {"title": _("Comment"), "missing": ""}}
    )

    private = Column(
        Boolean,
        info={
            "colanderalchemy": {
                "title": _("Private"),
                "widget": CheckboxWidget(item_css_class="item-private"),
            }
        },
    )
    author = Column(
        Enum(*tuple(USER_AUTHORS.keys()), native_enum=False, name="author"),
        nullable=False,
        default="new",
        info={"colanderalchemy": {"title": _("Author"), "widget": HiddenWidget()}},
    )
