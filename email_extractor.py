import re
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def extract_emails_from_site(url):
    if not url or url == "NO_WEBSITE":
        return ""

    if not url.startswith("http"):
        url = "http://" + url

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return ""

        # Using regex to find emails in the text
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = set(re.findall(email_pattern, response.text))
        
        # Check mailto links specifically
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if a['href'].startswith('mailto:'):
                email = a['href'].replace('mailto:', '').split('?')[0]
                emails.add(email)
        
        # Filter out common junk emails
        filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['example.com', 'sentry.io', 'wix.com', 'png', 'jpg'])]
        
        return ", ".join(filtered_emails) if filtered_emails else ""

    except Exception as e:
        logger.warning(f"Email extraction failed for {url}: {e}")
        return ""
