from pyramid.view import view_config, view_defaults

from getitfixed.views.admin.photos import PhotoViews


@view_defaults(match_param=("application=getitfixed_private", "table=photos"))
class PhotoViews(PhotoViews):
    @view_config(route_name="c2cgeoform_item", request_method="GET")
    def get(self):
        return super().get()
