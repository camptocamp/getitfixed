import pytest

from getitfixed.url import generate_url


@pytest.mark.usefixtures("app_env")
def test_generate_url(app_env):
    request = app_env["request"]
    assert "https://server.com/static/image.png" == generate_url(request, "https://server.com/static/image.png")
    assert "/static/image.png" == generate_url(request, "/static/image.png")
    assert "static/image.png" == generate_url(request, "static/image.png")
    assert "http://localhost/getitfixed_static/image.png" == generate_url(request, "getitfixed:static/image.png")
