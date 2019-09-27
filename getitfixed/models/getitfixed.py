# coding=utf-8
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, Enum, Integer, ForeignKey, String, Text
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.associationproxy import association_proxy

import geoalchemy2

import colander
from deform.widget import (
    FormWidget,
    HiddenWidget,
    SelectWidget,
    SequenceWidget,
    TextAreaWidget,
    TextInputWidget,
)
from c2cgeoform.ext.deform_ext import RelationSelectWidget

from c2cgeoform.ext import colander_ext, deform_ext
from c2cgeoform.models import FileData

from getitfixed.i18n import _
from getitfixed.models.meta import Base

schema = "getitfixed"

gmf_demo_map = """new ol.layer.Tile({
    source: new ol.source.WMTS({
        capabilities: "https://geomapfish-demo-2-4.camptocamp.com/tiles/1.0.0/WMTSCapabilities.xml",
        url: "https://geomapfish-demo-2-4.camptocamp.com/tiles/1.0.0/{Layer}/default/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.png",
        requestEncoding: "REST",
        layer: "map",
        matrixSet: "swissgrid_005",
        dimensions: {},
        style: "default",
        projection: new ol.proj.Projection({
            code: "EPSG:21781"
        }),
        tileGrid: new ol.tilegrid.WMTS({
            origin: [420000, 350000],
            resolutions: [1000, 500, 250, 100, 50, 20, 10, 5, 2, 1, 0.5, 0.25, 0.1, 0.05],
            matrixIds: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"],
        }),
        attributions: []
    })
})"""  # noqa


STATUSES = {
    "new": _("Nouveau"),
    "in_progress": _("In progress"),
    "waiting_for_customer": _("Waiting for customer"),
    "resolved": _("Resolved"),
}


# FIXME a file upload memory store is not appropriate for production
# See http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html#deform.interfaces.FileUploadTempStore  # noqa
class FileUploadTempStore(dict):
    def preview_url(self, name):
        return None


_file_upload_temp_store = FileUploadTempStore()


class Photo(FileData, Base):
    __tablename__ = "photo"
    __table_args__ = {"schema": schema}
    # Setting unknown to 'preserve' is required in classes used as a
    # FileUpload field.
    __colanderalchemy_config__ = {
        "title": _("Photo"),
        "unknown": "preserve",
        "widget": deform_ext.FileUploadWidget(_file_upload_temp_store),
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
        info={"colanderalchemy": {"title": _("Email"), "widget": TextInputWidget()}},
    )


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
    description = Column(
        Text,
        nullable=False,
        info={
            "colanderalchemy": {
                "title": _("Description"),
                "widget": TextAreaWidget(rows=3),
            }
        },
    )
    localisation = Column(
        String(254),
        nullable=False,
        info={"colanderalchemy": {"title": _("Localisation")}},
    )
    geometry = Column(
        geoalchemy2.Geometry("POINT", 4326, management=True),
        info={
            "colanderalchemy": {
                "title": _("Position"),
                "typ": colander_ext.Geometry("POINT", srid=4326, map_srid=3857),
                "widget": deform_ext.MapWidget(
                    base_layer=gmf_demo_map,
                    center=[738260, 5864270],
                    zoom=12,
                    item_css_class="item-geometry",
                ),
            }
        },
    )
    photos = relationship(
        Photo,
        cascade="all, delete-orphan",
        info={"colanderalchemy": {"title": _("Photo")}},
    )
    firstname = Column(
        String(100), nullable=False, info={"colanderalchemy": {"title": _("Firstname")}}
    )
    lastname = Column(
        String(100), nullable=False, info={"colanderalchemy": {"title": _("Lastname")}}
    )
    phone = Column(
        String(20), nullable=False, info={"colanderalchemy": {"title": _("Phone")}}
    )
    email = Column(
        String(100),
        nullable=False,
        info={"colanderalchemy": {"title": _("Email"), "validator": colander.Email()}},
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
    category = association_proxy("type", "category")


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
