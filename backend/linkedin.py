"""
linkedin.py
Pulls public job postings from LinkedIn's guest job-search listing page.

NOTE: This hits LinkedIn's public, unauthenticated "jobs-guest" search page
(no login/session, no bypassing any auth or paywall) -- the same page a
signed-out visitor sees in a browser. LinkedIn's Terms of Service restrict
automated scraping, so:
  - keep request volume low and add delays/backoff in production,
  - consider this a prototype/dev data source, and
  - for anything production-facing, use an official job-listing API
    (e.g. LinkedIn's Jobs API via partnership, Adzuna, Indeed's API, etc.)
    instead -- swap the implementation below, the rest of the app doesn't
    care where `search_jobs()` gets its data from.
"""

import requests
from bs4 import BeautifulSoup
from config import Config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def search_jobs(keywords, location=None, limit=25):
    location = location or Config.JOB_SEARCH_LOCATION_DEFAULT
    jobs = []
    start = 0

    while len(jobs) < limit and start < 200:  # hard stop to avoid hammering the endpoint
        params = {"keywords": keywords, "location": location, "start": start}
        try:
            resp = requests.get(
                Config.LINKEDIN_SEARCH_URL, params=params, headers=HEADERS, timeout=10
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"LinkedIn fetch failed: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("li")
        if not cards:
            break

        for card in cards:
            title_el = card.find("h3", class_="base-search-card__title")
            company_el = card.find("h4", class_="base-search-card__subtitle")
            location_el = card.find("span", class_="job-search-card__location")
            link_el = card.find("a", class_="base-card__full-link")
            if not title_el or not link_el:
                continue

            jobs.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "location": location_el.get_text(strip=True) if location_el else "",
                "url": link_el["href"].split("?")[0],
                # the guest listing page doesn't expose full descriptions;
                # title is used as a lightweight stand-in for matching
                "description": title_el.get_text(strip=True),
            })
            if len(jobs) >= limit:
                break

        start += 25

    return jobs