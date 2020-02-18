from mimetypes import guess_type

from pyramid.view import view_config, view_defaults

from c2cgeoform.views.abstract_views import AbstractViews

from getitfixed.models.getitfixed import Photo


@view_defaults(
    match_param=("application=getitfixed_admin", "table=photos"),
    permission="getitfixed_admin",
)
class PhotoViews(AbstractViews):

    _model = Photo
    _id_field = "id"

    @view_config(route_name="c2cgeoform_item", request_method="GET")
    def get(self):
        obj = self._get_object()
        response = self._request.response
        response.body = obj.data
        response.content_type = guess_type(obj.filename)[0]
        return response
