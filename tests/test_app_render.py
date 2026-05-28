"""Render-layer test for app.py.

Streamlit and the option menu are replaced with mocks so the module's
top-level UI code can be exercised without a browser or network access.
"""

import sys
from unittest import mock

import pytest


@pytest.fixture
def imported_app(monkeypatch):
    """Import app.py fresh with Streamlit mocked. Returns the streamlit mock."""
    st = mock.MagicMock()
    option_menu_mod = mock.MagicMock()
    # Returning a value that matches no tab means no data-fetch branch runs,
    # so importing the module performs no network I/O.
    option_menu_mod.option_menu.return_value = ""

    monkeypatch.setitem(sys.modules, "streamlit", st)
    monkeypatch.setitem(sys.modules, "streamlit_option_menu", option_menu_mod)
    sys.modules.pop("app", None)
    import app  # noqa: F401

    yield st
    sys.modules.pop("app", None)


def test_app_configures_page_and_renders_header(imported_app):
    st = imported_app
    st.set_page_config.assert_called_once()
    assert st.title.called
    assert st.header.called
    assert st.balloons.called


def test_app_does_no_io_when_no_tab_selected(imported_app):
    st = imported_app
    # No tab matched, so nothing should have been rendered into a container.
    assert not st.image.called
    assert not st.video.called


def test_app_wires_all_menu_tabs(monkeypatch):
    """Each menu selection should drive the matching renderer."""
    cases = {
        "Cats": ("get_cat", {"image": "i", "breed": "b"}),
        "Dogs": ("get_dog", {"image": "i", "breed": "b"}),
        "Memes": ("get_meme", {"title": "t", "url": "u", "ups": 1,
                               "subreddit": "s", "author": "a", "postLink": "l"}),
    }
    for tab, (func_name, payload) in cases.items():
        st = mock.MagicMock()
        option_menu_mod = mock.MagicMock()
        option_menu_mod.option_menu.return_value = tab
        monkeypatch.setitem(sys.modules, "streamlit", st)
        monkeypatch.setitem(sys.modules, "streamlit_option_menu", option_menu_mod)
        sys.modules.pop("app", None)
        with mock.patch(f"birthday_api.{func_name}", return_value=payload) as fn:
            import app  # noqa: F401
        assert fn.called, f"{func_name} should be called for the {tab} tab"
        assert st.image.called, f"an image should render for the {tab} tab"
        sys.modules.pop("app", None)
