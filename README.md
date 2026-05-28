# 🎂 Happy Birthday, Liz! — A Personalized Streamlit Surprise

<div align="center">

  ![Python](https://img.shields.io/badge/python-v3.13-blue.svg)
  ![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B.svg)
  ![Heroku](https://img.shields.io/badge/Heroku--26-Cloud%20Deploy-purple.svg)
  ![Docker](https://img.shields.io/badge/Docker-Container-2496ED.svg)
  ![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20selenium-0A9EDC.svg)

  *A playful single-page Streamlit web app that delivers a birthday greeting and an endless stream of cats, dogs, wholesome memes, video games, and Proverbs — each pulled live from a public API.*

</div>

## 📋 Overview

This is a small, self-contained [Streamlit](https://streamlit.io/) application built as a personalized birthday gift. It opens with a celebratory greeting (complete with balloons 🎈) and a horizontal navigation menu that lets the visitor flip between five themed tabs. Each tab fetches fresh content on demand from a different public web API.

### ☁️ Deployment Platform
- 🟣 **Heroku** (heroku-26 stack, Python 3.13) — primary deployment via `Procfile` + `setup.sh`
- 🐳 **Docker** — `Dockerfile` for containerized runs
- 🎈 **Fly.io** — `fly.toml` for an alternative buildpack deploy

### ✨ Key Features

- 🐱 **Cats** — a random cat photo (with breed when known) from The Cat API
- 🐕 **Dogs** — a random dog photo (with breed when known) from The Dog API
- 😄 **Memes** — a fresh wholesome meme from Reddit via the Meme API
- 🎮 **Games** — a random highly-rated video game with cover art, summary, and trailer via Twitch/IGDB
- 📕 **Proverbs** — a random verse from the Book of Proverbs (ESV passage + Chinese CUVS translation)
- 🎨 **Custom theming** — dark navy palette with a pink accent, configured in `.streamlit/config.toml`
- 🧭 **Horizontal option menu** — Bootstrap-icon tabs powered by `streamlit-option-menu`
- 🧪 **Full test suite** — deterministic offline unit tests, a render-layer smoke test, and live Selenium end-to-end tests

---

## 📑 Table of Contents

- [📋 Overview](#-overview)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [🏗️ Architecture](#️-architecture)
- [📊 Application Tabs](#-application-tabs)
- [🔌 Data Sources & API Integration](#-data-sources--api-integration)
- [🧪 Testing](#-testing)
- [☁️ Deployment](#️-deployment)
- [📚 External Resources](#-external-resources)
- [👨‍💻 Author & Contact](#-author--contact)
- [⚠️ Disclaimer](#️-disclaimer)
- [📄 License](#-license)

---

## 🚀 Quick Start Guide

Get the birthday app running locally in a couple of minutes.

<details>
<summary><strong>📋 Prerequisites</strong></summary>

<div style="padding-left: 20px;">

- Python 3.13 (any 3.10+ works locally; the deploy target is 3.13)
- `pip` and a virtual environment tool (`venv` is fine)
- Internet access — every tab calls a live third-party API
- (Optional) Google Chrome — only needed to run the Selenium end-to-end tests

</div>
</details>

<details>
<summary><strong>🛠️ Installation Steps</strong></summary>

<div style="padding-left: 20px;">

### 1. Clone the repository

```bash
git clone <repository-url>
cd liz-birthday26
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` is the single source of dependencies — it includes both the
runtime packages (Streamlit, Requests, BeautifulSoup, the option menu) and the
test packages (pytest, Selenium).

### 3. Run the app

```bash
streamlit run app.py
```

Streamlit prints a local URL (default `http://localhost:8501`). Open it in your
browser and the birthday page loads with the **Cats** tab selected.

</div>
</details>

<details>
<summary><strong>🎨 Theming</strong></summary>

<div style="padding-left: 20px;">

The look and feel is defined in `.streamlit/config.toml`:

| Setting | Value | Meaning |
|---|---|---|
| `primaryColor` | `#E694FF` | Pink accent for interactive elements |
| `backgroundColor` | `#00172B` | Dark navy main background |
| `secondaryBackgroundColor` | `#0083B8` | Blue for widgets / sidebar |
| `textColor` | `#FFF` | White body text |
| `font` | `sans serif` | Base font family |

On Heroku, `setup.sh` regenerates an equivalent `~/.streamlit/config.toml` at
boot and wires the server to the platform-assigned `$PORT` in headless mode.

</div>
</details>

---

## 🏗️ Architecture

The project is intentionally tiny: a UI layer (`app.py`) on top of a pure,
network-only data layer (`birthday_api.py`). Keeping the data functions free of
any Streamlit import is what makes them unit-testable offline.

<details>
<summary><strong>📁 Project Structure</strong></summary>

<div style="padding-left: 20px;">

```
liz-birthday26/
├── 🐍 app.py                 # Streamlit UI: page config, menu, per-tab rendering
├── 🐍 birthday_api.py        # Data layer: get_cat / get_dog / get_meme / get_game / get_proverb
├── 🧪 conftest.py            # Shared pytest fixtures (FakeResponse helper)
├── 🧪 pytest.ini             # pytest config + the `e2e` marker
├── 🧪 tests/
│   ├── test_birthday_api.py  # Offline unit tests (network + randomness mocked)
│   ├── test_app_render.py    # Render-layer smoke test (Streamlit mocked)
│   └── test_e2e.py           # Selenium browser tests against a live server
├── 📦 requirements.txt       # Runtime + test dependencies (single file)
├── 🐍 .python-version        # Python 3.13 (Heroku + pyenv)
├── 🚀 Procfile               # Heroku web process
├── 🐚 setup.sh               # Heroku Streamlit config + $PORT wiring
├── 🐳 Dockerfile             # Container image (python:3.13)
├── 🎈 fly.toml               # Fly.io deploy config
├── 🎨 .streamlit/config.toml # Theme
└── 📓 Liz_Birthday.ipynb     # Original prototyping notebook
```

</div>
</details>

<details>
<summary><strong>🧩 Core Files</strong></summary>

<div style="padding-left: 20px;">

| File | Responsibility |
|---|---|
| `app.py` | Sets the page config, injects CSS, renders the title/greeting/balloons, builds the horizontal option menu, and dispatches to the matching renderer for the selected tab. |
| `birthday_api.py` | Houses the five data-fetching functions. No Streamlit dependency, so it can be imported and tested in isolation. |
| `conftest.py` | Lives at the repo root so the project is importable in tests; provides the `FakeResponse` stand-in for `requests.Response`. |
| `tests/` | The three-layer test suite (unit → render → end-to-end). |

</div>
</details>

<details>
<summary><strong>🔄 Request Flow</strong></summary>

<div style="padding-left: 20px;">

1. The browser loads `app.py`; Streamlit renders the greeting and the option menu.
2. The visitor selects a tab (or keeps the default **Cats**).
3. `app.py` calls the matching function in `birthday_api.py`.
4. That function issues one or more HTTP requests to a public API and normalizes the JSON/HTML into a small dictionary.
5. `app.py` renders the result — an image, text, and/or an embedded video.
6. Clicking the tab's button re-runs the script and fetches fresh content.

</div>
</details>

---

## 📊 Application Tabs

The horizontal menu (built with `streamlit-option-menu`) exposes five tabs, each
backed by a function in `birthday_api.py`.

<details>
<summary><strong>🐱 Cats</strong></summary>

<div style="padding-left: 20px;">

- **Function:** `get_cat()`
- **Source:** The Cat API (`api.thecatapi.com`)
- **Renders:** the cat's breed (or `?` when unknown) as a header, plus the image.
- Returns `{"image": <url>, "breed": <name|"?">}`.

</div>
</details>

<details>
<summary><strong>🐕 Dogs</strong></summary>

<div style="padding-left: 20px;">

- **Function:** `get_dog()`
- **Source:** The Dog API (`api.thedogapi.com`)
- **Renders:** the dog's breed (or `?`) as a header, plus the image.
- Returns `{"image": <url>, "breed": <name|"?">}`.

</div>
</details>

<details>
<summary><strong>😄 Memes</strong></summary>

<div style="padding-left: 20px;">

- **Function:** `get_meme()`
- **Source:** Meme API (`meme-api.com`), `wholesomememes` subreddit.
- **Renders:** the meme title, image, up-votes, subreddit, author, and post link.
- Returns the raw meme object from the API.

</div>
</details>

<details>
<summary><strong>🎮 Games</strong></summary>

<div style="padding-left: 20px;">

- **Function:** `get_game()`
- **Source:** Twitch OAuth → IGDB (`api.igdb.com`) game videos, games, and covers.
- **Flow:** authenticate with Twitch client credentials → pull a list of game videos → pick one at random → look up the game and its cover art.
- **Renders:** the game name, cover image, summary, and an embedded YouTube trailer.
- Returns `{"name", "cover", "summary", "video"}`.

</div>
</details>

<details>
<summary><strong>📕 Proverbs</strong></summary>

<div style="padding-left: 20px;">

- **Function:** `get_proverb(field="html")`
- **Source:** ESV API (`api.esv.org`) for the passage HTML, plus BibleGateway (scraped with BeautifulSoup) for the Chinese **CUVS** translation.
- **Flow:** pick a random chapter/verse within Proverbs' real chapter lengths → fetch the ESV passage → scrape the matching CUVS verse span.
- **Renders:** the ESV passage HTML followed by the Chinese translation.
- Returns `{"html": <response>, "translation": <text> }`.

</div>
</details>

---

## 🔌 Data Sources & API Integration

<details>
<summary><strong>🌐 APIs Used</strong></summary>

<div style="padding-left: 20px;">

| Tab | Service | Base URL | Auth |
|---|---|---|---|
| Cats | The Cat API | `https://api.thecatapi.com` | `x-api-key` header |
| Dogs | The Dog API | `https://api.thedogapi.com` | `x-api-key` header |
| Memes | Meme API | `https://meme-api.com` | none |
| Games | Twitch ID + IGDB | `https://id.twitch.tv`, `https://api.igdb.com` | OAuth client credentials → Bearer token |
| Proverbs | ESV API + BibleGateway | `https://api.esv.org`, `https://www.biblegateway.com` | ESV: `Authorization: Token`; BibleGateway: none |

</div>
</details>

<details>
<summary><strong>🔑 Credentials</strong></summary>

<div style="padding-left: 20px;">

> **Heads up:** the current code ships API keys inline in `birthday_api.py`. That
> was fine for a one-off personal gift, but for any public or shared deployment
> these should be moved to environment variables / Streamlit secrets and the
> existing keys rotated. The data functions are already isolated, so swapping the
> literals for `os.environ[...]` lookups is a localized change.

</div>
</details>

---

## 🧪 Testing

The suite is layered so most of it runs fast and offline, while the browser tests
verify the real, fully-rendered app.

<details>
<summary><strong>🗂️ Test Suites</strong></summary>

<div style="padding-left: 20px;">

| File | Layer | What it covers | Network? |
|---|---|---|---|
| `tests/test_birthday_api.py` | Unit | Every data function — URL/auth construction, JSON parsing, breed fallback (`?`), game cover/video assembly, proverb scraping + CUVS formatting. `requests` and `random` are mocked. | No (mocked) |
| `tests/test_app_render.py` | Render | Imports `app.py` with Streamlit mocked; verifies page config, header/balloons, that no I/O happens when no tab matches, and that each tab drives the right renderer. | No (mocked) |
| `tests/test_e2e.py` | End-to-end | Launches a real `streamlit run app.py` server and drives headless Chrome via Selenium: homepage header, all five menu tabs, the Cats image, and navigating to the Memes tab. | Yes (live) |

</div>
</details>

<details>
<summary><strong>▶️ Running the Tests</strong></summary>

<div style="padding-left: 20px;">

```bash
# Everything except the browser tests (fast, offline)
pytest -m "not e2e"

# Only the Selenium end-to-end tests (needs Chrome + network)
pytest -m e2e

# The whole suite
pytest
```

The `e2e` marker is registered in `pytest.ini`. The end-to-end tests **skip
cleanly** when Streamlit, Selenium, or a usable Chrome/driver are unavailable, so
the offline tests always run regardless of environment.

</div>
</details>

---

## ☁️ Deployment

<details>
<summary><strong>🟣 Heroku (heroku-26 / Python 3.13)</strong></summary>

<div style="padding-left: 20px;">

The app targets the **heroku-26** stack. Python is pinned via `.python-version`
(`3.13`) — Heroku has deprecated `runtime.txt` in favor of this file.

- `Procfile` defines the web process:

  ```
  web: sh setup.sh && streamlit run app.py
  ```

- `setup.sh` writes a Streamlit config at boot, binding to the Heroku-assigned
  `$PORT` in headless mode.

```bash
heroku stack:set heroku-26 -a <app-name>
git push heroku main
```

</div>
</details>

<details>
<summary><strong>🐳 Docker</strong></summary>

<div style="padding-left: 20px;">

```bash
docker build -t liz-birthday .
docker run -p 8501:8501 -e PORT=8501 liz-birthday
```

The image is based on `python:3.13`, installs `requirements.txt`, and launches
via `setup.sh` + `streamlit run app.py`.

</div>
</details>

<details>
<summary><strong>🎈 Fly.io</strong></summary>

<div style="padding-left: 20px;">

`fly.toml` is configured for the `paketobuildpacks/builder:base` builder with an
internal port of `8080`. Deploy with:

```bash
fly deploy
```

</div>
</details>

---

## 📚 External Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [streamlit-option-menu](https://github.com/victoryhb/streamlit-option-menu)
- [The Cat API](https://thecatapi.com/)
- [The Dog API](https://thedogapi.com/)
- [Meme API](https://github.com/D3vd/Meme_Api)
- [IGDB API](https://api-docs.igdb.com/)
- [Twitch Authentication](https://dev.twitch.tv/docs/authentication/)
- [ESV API](https://api.esv.org/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium with Python](https://selenium-python.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)

---

## 👨‍💻 Author & Contact

**Tyler Potts** - *Developer*

- 📧 **Email**: [twpotts11@gmail.com](mailto:twpotts11@gmail.com)
- 💼 **Upwork**: [Professional Profile](https://www.upwork.com/freelancers/robotraderguy)
- 🔗 **LinkedIn**: [Tyler Potts](https://www.linkedin.com/in/tyler-potts-022b6573/)

---

## ⚠️ Disclaimer

This app displays content fetched live from third-party public APIs and is provided
as-is, for personal and educational use. The maintainer does not control and is not
responsible for the external content returned by those services. API keys committed
to this repository should be treated as compromised and rotated before any public
deployment.

---

## 📄 License

This project is proprietary software. All rights reserved. Unauthorized distribution
or modification is prohibited.

---

<div align="center">

**Built with ❤️ for Liz**

🎂 🎈 🐱 🐕 😄 🎮 📕

</div>
