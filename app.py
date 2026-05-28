# Import packages

import json
import streamlit as st
from streamlit_option_menu import option_menu

from birthday_api import get_cat, get_dog, get_meme, get_game, get_proverb

# Set page config

st.set_page_config(page_title="Happy birthday, Liz!", page_icon=":birthday:", layout="wide")
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

# Remove whitespace from the top of the page and sidebar

whitespace_style = \
    """
    <style>
        .css-18e3th9 {
                padding-top: 0rem;
                padding-bottom: 10rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
        .css-1d391kg {
                padding-top: 3rem;
                padding-right: 1rem;
                padding-bottom: 3rem;
                padding-left: 1rem;
            }
        .css-hxt7ib {
                padding-top: 3rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
        .css-r4g17z {
                height: 2rem;
            }
    </style>
    """
st.markdown(whitespace_style, unsafe_allow_html=True)

# Title of page

st.title(":birthday: Happy Birthday, Liz!")
# st.markdown("<h1 style='text-align: center; color: grey;'>Big headline</h1>", unsafe_allow_html=True)
st.markdown("##")
st.header("我很喜欢你，很重视你，很想见到你 🙂 - 彭天睿")
st.balloons()

# Option Menu

page_options = ["Cats", "Dogs", "Memes", "Games", "Proverbs"]
page_icons = ["bullseye", "stars", "reddit", "steam", "shield-plus"]
selected_menu = option_menu(
        menu_title=None,  # required
        options=page_options,  # required
        icons=page_icons,  # optional https://icons.getbootstrap.com/
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
        styles = {
            "container": {
                "padding": "0!important", 
                "background-color": "black"
            },
            "icon": {
                "color": "orange", 
                "font-size": "25px"
            },
            "nav-link": {
                "font-size": "25px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "gray",
            },
            "nav-link-selected": {
                "background-color": "#0083B8"
            },
        },
    )

if selected_menu == "Cats":

    button = st.button(
        label = "另外一个猫🐱",
        on_click = get_cat
    )
    with st.container():
        cat = get_cat()
        st.header(f'Breed: {cat["breed"]}')
        st.image(cat["image"])

elif selected_menu == "Dogs":

    button = st.button(
        label = "另外一个狗🐕",
        on_click = get_dog
    )
    with st.container():
        dog = get_dog()
        st.header(f'Breed: {dog["breed"]}')
        st.image(dog["image"])

elif selected_menu == "Memes":

    button = st.button(
        label = "另外一个meme😄",
        on_click = get_meme
    )
    with st.container():
        meme = get_meme()
        st.header(f"Title: {meme['title']}")
        st.image(meme['url'])
        st.write(f"Up-votes: {meme['ups']}")
        st.write(f"Subreddit: {meme['subreddit']}")
        st.write(f"Author: {meme['author']}")
        st.write(f"Link: {meme['postLink']}")

elif selected_menu == "Games":

    button = st.button(
        label = "另外一个游戏💻",
        on_click = get_game
    )
    with st.container():
        game = get_game()
        st.header(game["name"])
        st.image(game["cover"])
        st.write(game["summary"])
        st.video(game["video"])

elif selected_menu == "Proverbs":

    button = st.button(
        label = "另外一个箴言📕",
        on_click = get_proverb
    )
    with st.container():
        proverb = get_proverb("html")
        proverb_html = json.loads(proverb["html"].content)['passages'][0]
        st.markdown(proverb_html, unsafe_allow_html=True)
        st.write(proverb["translation"])
        # proverb = get_proverb("audio")
        # st.audio(proverb)


# Memes

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = \
    """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)