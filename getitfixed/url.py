from urllib.parse import urlparse


def generate_url(request, url_definition):
    o = urlparse(url_definition)

    if o.scheme != "" and o.netloc != "":
        # Definition is an absolute url ex: https://server.com/static/image.png
        return url_definition

    if o.scheme == "" and o.netloc == "":
        # Definition is a relative url ex: static/image.png or /static/image.png
        return url_definition

    if o.scheme != "" and o.netloc == "":
        # Definition is a static path ex: getitfixed:static/image.png
        return request.static_url(url_definition)
