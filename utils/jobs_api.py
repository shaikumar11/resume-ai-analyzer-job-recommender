import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

# Sign up free at https://jooble.org/api/about — Jooble aggregates postings
# from many original boards (company sites, Indeed, Naukri, sometimes
# LinkedIn), so its "apply" links often lead straight back to those sites.
# This is the legitimate way to get that coverage — LinkedIn/Naukri have no
# public search API, and scraping them directly would violate their ToS.
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")
JOOBLE_URL = f"https://jooble.org/api/{JOOBLE_API_KEY}" if JOOBLE_API_KEY else None


def _fetch_adzuna(query, location, results_count):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_count,
        "what": query,
        "content-type": "application/json",
    }
    if location:
        params["where"] = location

    try:
        response = requests.get(ADZUNA_URL, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return []

    jobs = []
    for item in data.get("results", []):
        jobs.append({
            "id": f"adzuna-{item.get('id')}",
            "title": item.get("title", "Untitled Role"),
            "company": item.get("company", {}).get("display_name", "Unknown Company"),
            "description": item.get("description", ""),
            "redirect_url": item.get("redirect_url", "#"),
            "location": item.get("location", {}).get("display_name", ""),
            "contract_time": item.get("contract_time", ""),
            "category": item.get("category", {}).get("label", ""),
            "created": item.get("created", ""),
            "source": "Adzuna",
        })
    return jobs


def _fetch_jooble(query, location, results_count):
    if not JOOBLE_URL:
        return []

    payload = {"keywords": query, "location": location or "India"}

    try:
        response = requests.post(JOOBLE_URL, json=payload, timeout=6)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return []

    jobs = []
    for item in data.get("jobs", [])[:results_count]:
        jobs.append({
            "id": f"jooble-{abs(hash(item.get('link', '')))}",
            "title": item.get("title", "Untitled Role"),
            "company": item.get("company") or "Unknown Company",
            "description": item.get("snippet", ""),
            "redirect_url": item.get("link", "#"),
            "location": item.get("location", ""),
            "contract_time": (item.get("type") or "").strip().lower().replace(" ", "_"),
            "category": "",
            "created": item.get("updated", ""),
            "source": "Jooble",
        })
    return jobs


def fetch_live_jobs(query="software developer", location="", results_count=5):
    """
    Fetch jobs from Adzuna and Jooble in parallel, then merge and de-dupe.
    Same return shape as before (list of dicts with title/company/etc.),
    plus a new "source" field per job.
    """
    if not ADZUNA_APP_ID and not JOOBLE_URL:
        raise ValueError(
            "No job API credentials configured. Set ADZUNA_APP_ID/ADZUNA_APP_KEY "
            "and/or JOOBLE_API_KEY in your .env file."
        )

    per_source = max(3, results_count // 2 + 2)
    all_jobs = []

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(_fetch_adzuna, query, location, per_source): "adzuna",
            pool.submit(_fetch_jooble, query, location, per_source): "jooble",
        }
        for future in as_completed(futures, timeout=10):
            try:
                all_jobs.extend(future.result())
            except Exception:
                continue

    # de-dupe by (title, company) case-insensitive — two sources can
    # legitimately return the same posting
    seen = set()
    deduped = []
    for job in all_jobs:
        key = (job["title"].strip().lower(), job["company"].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)

    return deduped[:results_count]