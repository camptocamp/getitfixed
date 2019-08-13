# coding=utf-8
from uuid import uuid4

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    ForeignKey)
from sqlalchemy.orm import relationship

import geoalchemy2
import deform
from deform.widget import HiddenWidget
from c2cgeoform.ext import colander_ext, deform_ext
from c2cgeoform.models import FileData

from getitfixed.i18n import _
from getitfixed.models.meta import Base


schema = 'getitfixed'


# FIXME a file upload memory store is not appropriate for production
# See http://docs.pylonsproject.org/projects/deform/en/latest/interfaces.html#deform.interfaces.FileUploadTempStore  # noqa
class FileUploadTempStore(dict):
    def preview_url(self, name):
        return None


_file_upload_temp_store = FileUploadTempStore()


class Photo(FileData, Base):
    __tablename__ = 'photo'
    __table_args__ = (
        {"schema": schema}
    )
    # Setting unknown to 'preserve' is required in classes used as a
    # FileUpload field.
    __colanderalchemy_config__ = {
        'title': _('Photo'),
        'unknown': 'preserve',
        'widget': deform_ext.FileUploadWidget(_file_upload_temp_store)
    }
    issue_id = Column(Integer, ForeignKey('{}.issue.id'.format(schema)))


# This is the main model class which is used to register a schema.
class Issue(Base):
    __tablename__ = 'issue'
    __table_args__ = (
        {"schema": schema}
    )
    __colanderalchemy_config__ = {
        'title': _('Issue'),
        'plural': _('Issues')
    }

    id = Column(Integer, primary_key=True, info={
        # the `colanderalchemy` property allows to set a custom title for the
        # column or to use a specific widget.
        'colanderalchemy': {
            'title': _('Identifier'),
            'widget': HiddenWidget()
        }})
    hash = Column(Text, unique=True, default=lambda: str(uuid4()), info={
        'colanderalchemy': {
            'widget': HiddenWidget()
        },
        'c2cgeoform': {
            'duplicate': False
        }})
    request_date = Column(Date, nullable=True, info={
        'colanderalchemy': {
            'title': _('Request Date')
        }})
    description = Column(Text, nullable=True, info={
        'colanderalchemy': {
            'title': _('Description of the Work'),
            'description': _('exemple de description'),
            'widget': deform.widget.TextAreaWidget(rows=3),
        }})
    geometry = Column(
        geoalchemy2.Geometry('POINT', 4326, management=True), info={
            'colanderalchemy': {
                'title': _('Position'),
                'typ':
                colander_ext.Geometry('POINT', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})
    photos = relationship(
        Photo,
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': _('Photo')
            }})
