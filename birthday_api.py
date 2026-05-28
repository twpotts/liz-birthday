"""Data-fetching helpers for the birthday app.

These functions are kept free of any Streamlit dependency so they can be
unit-tested in isolation (see tests/). app.py imports and renders them.

Note: the API keys below are committed to source control. They should be
moved to environment variables / Streamlit secrets before any public use.
"""

# Import packages

from bs4 import BeautifulSoup
import json
import random
import requests


def get_cat():
    cat_api = "live_avHGVDMcqdtgn1MlGH97LTsZ9jboFLHKcj3GXTQB4hfdzRPE69VKL5jsbZUV5ymg"
    cat_headers = {
        "x-api-key": cat_api
    }
    cat_base = "https://api.thecatapi.com"
    cat_breed_id = ''
    cat_limit = 1
    cat_url = f"{cat_base}/v1/images/search?limit={cat_limit}&breed_ids={cat_breed_id}&api_key={cat_api}"
    cats = requests.get(cat_url, headers = cat_headers)
    cats = json.loads(cats.content)
    if cats[0]['breeds'] != []:
        breed = cats[0]['breeds'][0]['name']
    else:
        breed = "?"
    cat_dict = {
        "image": cats[0]['url'],
        "breed": breed
    }
    return cat_dict


def get_dog():
    dog_api = "live_vjor7WxklBzIDv5X6aBDzEdZ9ceu4Fmjint1lC8ztx3pjCnUC9aQqDu5WTkI12CB"
    dog_headers = {
        "x-api-key": dog_api
    }
    dog_base = "https://api.thedogapi.com"
    dog_breed_id = ""
    dog_limit = 1
    dog_url = f"{dog_base}/v1/images/search?limit={dog_limit}&breed_ids={dog_breed_id}&api_key={dog_api}"
    dogs = requests.get(dog_url, headers = dog_headers)
    dogs = json.loads(dogs.content)
    if dogs[0]["breeds"] != []:
        breed = dogs[0]['breeds'][0]['name']
    else:
        breed = "?"
    dogs_dict = {
        "image": dogs[0]['url'],
        "breed": breed
    }
    return dogs_dict


def get_meme():
    # meme_base = "https://meme-api.herokuapp.com"
    meme_base = "https://meme-api.com"
    subreddit = "wholesomememes" # Default = 'memes', 'dankmemes', 'me_irl'
    count = 1 # max = 50
    meme_url = f"{meme_base}/gimme/{subreddit}/{count}"
    memes = requests.get(meme_url)
    memes = json.loads(memes.content)['memes']
    meme = memes[0]
    return meme


def get_game():
    twitch_api = "zqvkd3br6bi91muh5zmohkeom04175"
    twitch_secret = "1dbgcndsadqy63uzg1lqm98jqreslx"
    twitch_base = "https://id.twitch.tv"
    twitch_auth_url = f"{twitch_base}/oauth2/token"
    params = {
        "client_id": twitch_api,
        "client_secret": twitch_secret,
        "grant_type": "client_credentials"
    }
    r = requests.post(twitch_auth_url, params = params)
    resp = json.loads(r.content)
    access_token = resp["access_token"]
    headers = {
        "Client-ID": twitch_api,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    igdb_base = "https://api.igdb.com"
    url2 = f"{igdb_base}/v4/game_videos"
    data2 = f'fields *; sort rating desc; limit 500;'
    r2 = requests.post(url2, headers = headers, data = data2)
    resp2 = json.loads(r2.content)
    idx = random.randint(0, len(resp2)-1)
    youtube = f"https://www.youtube.com/watch?v={resp2[idx]['video_id']}"
    game_id = resp2[idx]['game']
    url3 = f"{igdb_base}/v4/games"
    data3 = f'fields *; where id = {game_id};'
    r3 = requests.post(url3, headers = headers, data = data3)
    resp3 = json.loads(r3.content)[0]
    missing = "cover" not in resp3 or "name" not in resp3 or "summary" not in resp3
    if missing:
        print(resp3)
        while missing:
            idx = random.randint(0, len(resp3)-1)
            missing = "cover" not in resp3 or "name" not in resp3 or "summary" not in resp3
    cover_id = resp3['cover']
    url4 = f"{igdb_base}/v4/covers"
    data4 = f'fields *; where id = {cover_id};'
    r4 = requests.post(url4, headers = headers, data = data4)
    resp4 = json.loads(r4.content)[0]
    game_dict = {
        "name": resp3['name'],
        "cover": resp4['url'].replace("//","https://"),
        "summary": resp3['summary'],
        "video": youtube
    }
    return game_dict


def get_proverb(field="html"):
    esv_api = "f34d73c90921c9e47d306b3429c2caa3b38082c2"
    esv_base = "https://api.esv.org"
    CHAPTER_LENGTHS = [
        33, 22, 35, 27, 23, 35, 27, 36, 18, 32,
        31, 28, 25, 35, 33, 33, 28, 24, 29, 30,
        31, 29, 35, 34, 28, 28, 27, 28, 27, 33,
        31
    ]
    chapter = random.randrange(1, len(CHAPTER_LENGTHS))
    verse = random.randint(1, CHAPTER_LENGTHS[chapter])
    book = "Proverbs"
    lookup = f"{book}+{chapter}:{verse}"
    esv_verse = f"{esv_base}/v3/passage/{field}/?q={lookup}"
    headers = {
        "Authorization": f"Token {esv_api}"
    }
    r = requests.get(esv_verse, headers = headers)
    version = "CUVS"
    url = f"https://www.biblegateway.com/passage/?search={book}+{chapter}%3A{verse}&version={version}"
    r2 = requests.get(url)
    soup = BeautifulSoup(r2.content, "html.parser")
    v = soup.find("span", {"class": f"Prov-{chapter}-{verse}"}).text.replace("\xa0", " ")
    v = f"{v} ({version})"
    proverb_dict = {
        "html": r,
        "translation": v
    }
    return proverb_dict
