from urllib.parse import urlparse


def generate_url(request, url_definition):
    o = urlparse(url_definition)

    if o.scheme == "static":
        # Definition is a static path ex: static://getitfixed:static/image.png
        return request.static_url("{}{}".format(o.netloc, o.path))

    # Definition is an absolute url ex: https://server.com/static/image.png
    return url_definition
