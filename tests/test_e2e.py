"""End-to-end browser tests driven by Selenium against a live Streamlit server.

These spin up `streamlit run app.py` as a subprocess and drive a real headless
Chrome browser. They are marked `e2e` and skip cleanly when Streamlit, Selenium,
or a usable Chrome/driver are unavailable (e.g. in a headless CI without a
browser), so the rest of the suite still runs.

Run only these with:   pytest -m e2e
Skip them with:        pytest -m "not e2e"

Note: the tab tests below exercise the app's live external APIs (cats, dogs,
memes), so they require network access and valid API keys.
"""

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest

pytestmark = pytest.mark.e2e

# Skip the whole module if the e2e dependencies aren't importable.
pytest.importorskip("streamlit")
selenium = pytest.importorskip("selenium")

from selenium import webdriver  # noqa: E402
from selenium.common.exceptions import WebDriverException  # noqa: E402
from selenium.webdriver.chrome.options import Options  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_health(base_url, timeout=60):
    """Poll Streamlit's health endpoint until it reports ready."""
    deadline = time.monotonic() + timeout
    health = f"{base_url}/_stcore/health"
    last_err = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health, timeout=2) as resp:
                if resp.status == 200 and resp.read().strip() in (b"ok", b"\"ok\""):
                    return True
        except (urllib.error.URLError, ConnectionError, OSError) as exc:
            last_err = exc
            time.sleep(0.5)
    raise TimeoutError(f"Streamlit did not become healthy at {health}: {last_err}")


@pytest.fixture(scope="module")
def streamlit_server():
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless=true",
            "--server.port", str(port),
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats=false",
        ],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        try:
            _wait_for_health(base_url)
        except TimeoutError as exc:
            proc.terminate()
            out = b""
            try:
                out = proc.communicate(timeout=5)[0] or b""
            except subprocess.TimeoutExpired:
                proc.kill()
            pytest.skip(f"Could not start Streamlit server: {exc}\n{out.decode(errors='replace')}")
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,1200")
    try:
        drv = webdriver.Chrome(options=options)
    except WebDriverException as exc:
        pytest.skip(f"Chrome/chromedriver not available for Selenium: {exc}")
    drv.set_page_load_timeout(60)
    yield drv
    drv.quit()


def _body_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text


def _switch_to_menu_frame(driver, timeout=30):
    """The option menu renders in a Streamlit component iframe.

    Find and switch into the iframe that contains the menu labels. Returns True
    on success (driver is left inside the frame); raises TimeoutException if the
    menu never appears in any iframe.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        driver.switch_to.default_content()
        for frame in driver.find_elements(By.TAG_NAME, "iframe"):
            driver.switch_to.default_content()
            try:
                driver.switch_to.frame(frame)
                if "Cats" in driver.find_element(By.TAG_NAME, "body").text:
                    return True
            except WebDriverException:
                continue
        time.sleep(0.5)
    driver.switch_to.default_content()
    raise TimeoutError("option menu iframe with tab labels never appeared")


def test_homepage_renders_header(driver, streamlit_server):
    driver.get(streamlit_server)
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Happy Birthday, Liz!")
    )
    assert "Happy Birthday, Liz!" in _body_text(driver)


def test_all_menu_tabs_present(driver, streamlit_server):
    driver.get(streamlit_server)
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Happy Birthday, Liz!")
    )
    _switch_to_menu_frame(driver)
    menu_text = _body_text(driver)
    driver.switch_to.default_content()
    for tab in ("Cats", "Dogs", "Memes", "Games", "Proverbs"):
        assert tab in menu_text, f"expected menu tab {tab!r} to be visible"


def test_cats_tab_shows_breed_and_image(driver, streamlit_server):
    """Default tab is Cats; it should fetch a cat (live API) and show an image."""
    driver.get(streamlit_server)
    WebDriverWait(driver, 45).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Breed:")
    )
    images = driver.find_elements(By.CSS_SELECTOR, "img")
    assert images, "expected at least one rendered image on the Cats tab"


def test_navigate_to_memes_tab(driver, streamlit_server):
    """Clicking the Memes tab triggers a rerun and renders meme metadata."""
    driver.get(streamlit_server)
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Happy Birthday, Liz!")
    )
    # The clickable tab lives inside the option-menu component iframe.
    _switch_to_menu_frame(driver)
    link = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='Memes']"))
    )
    link.click()
    driver.switch_to.default_content()
    WebDriverWait(driver, 45).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Title:")
    )
    body = _body_text(driver)
    assert "Up-votes:" in body
    assert "Subreddit:" in body
