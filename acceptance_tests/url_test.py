import pytest
from pyramid import testing
from pyramid.paster import bootstrap

from getitfixed.url import generate_url


@pytest.mark.usefixtures("app_env")
def test_generate_url(app_env):
    request = app_env["request"]
    assert "https://server.com/static/image.png" == generate_url(request, "https://server.com/static/image.png")
    assert "/static/image.png" == generate_url(request, "/static/image.png")
    assert "static/image.png" == generate_url(request, "static/image.png")
    # Static url with explicit package name
    assert "http://localhost/getitfixed_static/image.png" == generate_url(request, "static://getitfixed:static/image.png")
    # Default to registry.package_name
    assert "http://localhost/getitfixed_static/image.png" == generate_url(request, "static://static/image.png")

def test_gmf_2_5():
    with bootstrap("tests.ini") as env:
        # Compatibility with GMF 2.5
        config = testing.setUp(registry=env["registry"])
        config.add_static_view(name="static", path="/etc/geomapfish/static")
        request = env["request"]
        assert "http://localhost/static/image.png" == generate_url(request, "static:///etc/geomapfish/static/image.png")
