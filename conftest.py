"""Shared pytest fixtures/helpers.

Placing this at the repo root puts the project root on sys.path so tests can
`import birthday_api` and `import app` directly.
"""

import json

import pytest


class FakeResponse:
    """Minimal stand-in for a requests.Response (only `.content` is used)."""

    def __init__(self, *, json_data=None, content=None):
        if content is not None:
            self.content = content
        else:
            self.content = json.dumps(json_data).encode("utf-8")


@pytest.fixture
def fake_response():
    return FakeResponse
