from io import BytesIO

import pytest
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.core.handlers.asgi import ASGIRequest

from config.asgi import application


def _static_request(path):
    return ASGIRequest(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [(b"host", b"localhost")],
            "client": ("127.0.0.1", 8000),
            "server": ("localhost", 8000),
            "root_path": "",
            "state": {},
        },
        BytesIO(),
    )


@pytest.mark.django_db
def test_debug_asgi_application_serves_django_admin_static_files():
    assert isinstance(application, ASGIStaticFilesHandler)

    request = _static_request("/static/admin/css/base.css")
    response = application.serve(request)

    try:
        assert response.status_code == 200
    finally:
        response.close()
