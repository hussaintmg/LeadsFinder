import requests
from bs4 import BeautifulSoup
import time
import logging
import re

logger = logging.getLogger(__name__)

def analyze_website_quality(url):

    if not url or url == "NO_WEBSITE":
        return "NO_WEBSITE", "No website found."

    if not url.startswith("http"):
        url = "http://" + url

    score = 100
    problems = []

    try:
        start = time.time()
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        load_time = time.time() - start

        if response.status_code != 200:
            return "NO_WEBSITE", f"Website returned status {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")

        # -------- SPEED CHECK --------
        if load_time > 4:
            score -= 15
            problems.append("Slow loading website")

        # -------- CONTENT QUALITY --------
        text = soup.get_text(separator=" ")
        word_count = len(text.split())

        if word_count < 300:
            score -= 20
            problems.append("Very low content")

        # -------- MOBILE RESPONSIVE --------
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            score -= 20
            problems.append("Not mobile responsive")

        # -------- SEO BASICS --------
        title = soup.find("title")
        meta_desc = soup.find("meta", attrs={"name": "description"})

        if not title:
            score -= 10
            problems.append("Missing page title")

        if not meta_desc:
            score -= 10
            problems.append("Missing meta description")

        # -------- NAVIGATION --------
        nav = soup.find("nav")
        if not nav:
            score -= 10
            problems.append("Weak navigation structure")

        # -------- IMAGES / DESIGN --------
        images = soup.find_all("img")
        if len(images) < 3:
            score -= 10
            problems.append("Very few images, weak design")

        # -------- CTA / CONTACT --------
        forms = soup.find_all("form")
        if len(forms) == 0:
            score -= 5
            problems.append("No contact form or lead capture")

        # -------- SOCIAL PROOF --------
        social_links = re.findall(r"(facebook|instagram|linkedin|twitter)", response.text, re.I)
        if not social_links:
            score -= 5
            problems.append("No social media integration")

        # -------- FINAL SCORE --------
        if score >= 75:
            status = "GOOD_WEBSITE"
        else:
            status = "WEAK_WEBSITE"

        problem_text = ", ".join(problems) if problems else "Website looks modern and well optimized."

        return status, f"Score: {score}/100 - {problem_text}"

    except Exception as e:
        logger.warning(f"Error analyzing {url}: {e}")
        return "WEAK_WEBSITE", "Site could not be fully analyzed."
