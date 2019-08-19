# coding=utf-8
from uuid import uuid4

from sqlalchemy import (
    Column,
    Date,
    Integer,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
import geoalchemy2

import colander
from deform.widget import HiddenWidget, TextAreaWidget, TextInputWidget
from c2cgeoform.ext.deform_ext import (
    RelationSelectWidget,
)

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


class Category(Base):
    __tablename__ = 'category'
    __table_args__ = (
        {"schema": schema}
    )
    __colanderalchemy_config__ = {
        'title': _('Category'),
        'plural': _('Categories')
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'title': _('Identifier'),
            'widget': HiddenWidget()
        }})
    label_fr = Column(String(50), info={
        'colanderalchemy': {
            'title': _('Label(fr)'),
            'widget': TextInputWidget(),
        }})
    label_en = Column(String(50), info={
        'colanderalchemy': {
            'title': _('Label(en)'),
            'widget': TextInputWidget(),
        }})


class Type(Base):
    __tablename__ = 'type'
    __table_args__ = (
        {"schema": schema}
    )
    __colanderalchemy_config__ = {
        'title': _('Type'),
        'plural': _('Types')
    }

    id = Column(Integer, primary_key=True, info={
        'colanderalchemy': {
            'title': _('Identifier'),
            'widget': HiddenWidget()
        }})
    label_fr = Column(String(50), info={
        'colanderalchemy': {
            'title': _('Label(fr)'),
            'widget': TextInputWidget(),
        }})
    label_en = Column(String(50), info={
        'colanderalchemy': {
            'title': _('Label(en)'),
            'widget': TextInputWidget(),
        }})
    category_id = Column(Integer, ForeignKey('{}.category.id'.format(schema)), info={
        'colanderalchemy': {
            'title': _('Category'),
            'widget': RelationSelectWidget(
                Category,
                'id',
                'label_fr',
                order_by='label_fr',
                default_value=('', _('- Select -'))
                )}})
    category = relationship(Category, backref='types')


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
    hash = Column(Text, nullable=False, unique=True, default=lambda: str(uuid4()), info={
        'colanderalchemy': {
            'exclude': True
        },
        'c2cgeoform': {
            'duplicate': False
        }})
    request_date = Column(Date, nullable=False, server_default=func.now(), info={
        'colanderalchemy': {
            'title': _('Request date'),
            'exclude': True
        }})
    type_id = Column(Integer, ForeignKey('{}.type.id'.format(schema)), nullable=False, info={
        'colanderalchemy': {
            'title': _('Type'),
            'widget': RelationSelectWidget(
                Type,
                'id',
                'label_fr',
                order_by='label_fr',
                default_value=('', _('- Select -'))
                )}})
    type = relationship(Type, info={
        'colanderalchemy': {
            'exclude': True
        }})
    description = Column(Text, nullable=False, info={
        'colanderalchemy': {
            'title': _('Description of the Work'),
            'widget': TextAreaWidget(rows=3),
        }})
    localisation = Column(String(254), nullable=False, info={
        'colanderalchemy': {
            'title': _('Localisation')
        }})
    geometry = Column(
        geoalchemy2.Geometry('POINT', 4326, management=True),
        info={
            'colanderalchemy': {
                'title': _('Position'),
                'typ': colander_ext.Geometry('POINT', srid=4326, map_srid=3857),
                'widget': deform_ext.MapWidget()
            }})
    photos = relationship(
        Photo,
        cascade="all, delete-orphan",
        info={
            'colanderalchemy': {
                'title': _('Photo')
            }})
    firstname = Column(String(100), nullable=False, info={
        'colanderalchemy': {
             'title': _('Firstname')
        }})
    lastname = Column(String(100), nullable=False, info={
        'colanderalchemy': {
             'title': _('Lastname')
        }})
    phone = Column(String(20), nullable=False, info={
        'colanderalchemy': {
            'title': _('Phone')
        }})
    email = Column(String(100), nullable=False, info={
        'colanderalchemy': {
            'title': _('Email'),
            'validator': colander.Email()
        }})
