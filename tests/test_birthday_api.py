"""Unit tests for the data-fetching helpers in birthday_api.

All network access (requests.get / requests.post) and randomness are mocked,
so these tests are deterministic and run offline.
"""

from unittest import mock

import pytest

import birthday_api
from conftest import FakeResponse


# --------------------------------------------------------------------------- #
# get_cat
# --------------------------------------------------------------------------- #
def test_get_cat_with_breed():
    payload = [{"url": "https://cdn/cat.jpg", "breeds": [{"name": "Persian"}]}]
    with mock.patch.object(
        birthday_api.requests, "get", return_value=FakeResponse(json_data=payload)
    ) as get:
        result = birthday_api.get_cat()

    assert result == {"image": "https://cdn/cat.jpg", "breed": "Persian"}
    # URL + auth are constructed correctly
    called_url = get.call_args.args[0]
    assert called_url.startswith("https://api.thecatapi.com/v1/images/search")
    assert "limit=1" in called_url
    assert get.call_args.kwargs["headers"]["x-api-key"]


def test_get_cat_without_breed():
    payload = [{"url": "https://cdn/cat.jpg", "breeds": []}]
    with mock.patch.object(
        birthday_api.requests, "get", return_value=FakeResponse(json_data=payload)
    ):
        result = birthday_api.get_cat()

    assert result["breed"] == "?"
    assert result["image"] == "https://cdn/cat.jpg"


# --------------------------------------------------------------------------- #
# get_dog
# --------------------------------------------------------------------------- #
def test_get_dog_with_breed():
    payload = [{"url": "https://cdn/dog.jpg", "breeds": [{"name": "Corgi"}]}]
    with mock.patch.object(
        birthday_api.requests, "get", return_value=FakeResponse(json_data=payload)
    ) as get:
        result = birthday_api.get_dog()

    assert result == {"image": "https://cdn/dog.jpg", "breed": "Corgi"}
    assert get.call_args.args[0].startswith("https://api.thedogapi.com/v1/images/search")


def test_get_dog_without_breed():
    payload = [{"url": "https://cdn/dog.jpg", "breeds": []}]
    with mock.patch.object(
        birthday_api.requests, "get", return_value=FakeResponse(json_data=payload)
    ):
        result = birthday_api.get_dog()

    assert result["breed"] == "?"


# --------------------------------------------------------------------------- #
# get_meme
# --------------------------------------------------------------------------- #
def test_get_meme():
    meme = {
        "title": "Good boy",
        "url": "https://cdn/meme.png",
        "ups": 1234,
        "subreddit": "wholesomememes",
        "author": "someone",
        "postLink": "https://reddit.com/x",
    }
    payload = {"memes": [meme]}
    with mock.patch.object(
        birthday_api.requests, "get", return_value=FakeResponse(json_data=payload)
    ) as get:
        result = birthday_api.get_meme()

    assert result == meme
    assert get.call_args.args[0] == "https://meme-api.com/gimme/wholesomememes/1"


# --------------------------------------------------------------------------- #
# get_game
# --------------------------------------------------------------------------- #
def test_get_game():
    responses = [
        FakeResponse(json_data={"access_token": "tok123"}),               # auth
        FakeResponse(json_data=[{"video_id": "abc", "game": 42}]),         # game_videos
        FakeResponse(json_data=[{"cover": 7, "name": "Hollow Knight",
                                 "summary": "Explore caves."}]),          # games
        FakeResponse(json_data=[{"url": "//images.igdb.com/cover.jpg"}]),  # covers
    ]
    with mock.patch.object(birthday_api.requests, "post", side_effect=responses) as post, \
            mock.patch.object(birthday_api.random, "randint", return_value=0):
        result = birthday_api.get_game()

    assert result == {
        "name": "Hollow Knight",
        "cover": "https://images.igdb.com/cover.jpg",
        "summary": "Explore caves.",
        "video": "https://www.youtube.com/watch?v=abc",
    }
    # First call authenticates against twitch with client_credentials
    auth_params = post.call_args_list[0].kwargs["params"]
    assert auth_params["grant_type"] == "client_credentials"
    assert auth_params["client_id"]
    assert post.call_count == 4


# --------------------------------------------------------------------------- #
# get_proverb
# --------------------------------------------------------------------------- #
def test_get_proverb():
    esv = FakeResponse(content=b'{"passages": ["<p>verse html</p>"]}')
    biblegateway = FakeResponse(
        content=b'<span class="Prov-1-1">Trust\xc2\xa0in\xc2\xa0the\xc2\xa0LORD</span>'
    )
    with mock.patch.object(
        birthday_api.requests, "get", side_effect=[esv, biblegateway]
    ) as get, \
            mock.patch.object(birthday_api.random, "randrange", return_value=1), \
            mock.patch.object(birthday_api.random, "randint", return_value=1):
        result = birthday_api.get_proverb()

    # The raw ESV response is passed through untouched for the app to render.
    assert result["html"] is esv
    # Non-breaking spaces are normalised and the version is appended.
    assert result["translation"] == "Trust in the LORD (CUVS)"

    esv_url = get.call_args_list[0].args[0]
    assert "Proverbs+1:1" in esv_url
    assert "/passage/html/" in esv_url  # default field


def test_get_proverb_respects_field_argument():
    esv = FakeResponse(content=b'{"passages": ["x"]}')
    biblegateway = FakeResponse(content=b'<span class="Prov-2-3">word</span>')
    with mock.patch.object(
        birthday_api.requests, "get", side_effect=[esv, biblegateway]
    ) as get, \
            mock.patch.object(birthday_api.random, "randrange", return_value=2), \
            mock.patch.object(birthday_api.random, "randint", return_value=3):
        birthday_api.get_proverb("audio")

    assert "/passage/audio/" in get.call_args_list[0].args[0]
