import json
import os
import re

import requests


SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen_usernames.json")


def _load_seen() -> set[str]:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def _save_seen(seen: set[str]):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen), f)


# Set to track already-seen usernames (persisted to disk)
seen_usernames: set[str] = _load_seen()

# Pattern: https://asi1.ai/ai/<username> with optional trailing slash and query params
LINK_PATTERN = re.compile(r"^https?://asi1\.ai/ai/([a-zA-Z0-9_-]+)/?(?:\?.*)?$")


def validate_link(link: str) -> tuple[bool, str]:
    """
    Validate an asi1.ai profile link.

    Returns:
        (is_valid, message) tuple
    """
    link = link.strip()

    match = LINK_PATTERN.match(link)
    if not match:
        return False, "Invalid link. Must be in the format: https://asi1.ai/ai/<username>"

    username = match.group(1).lower()

    # Block example/placeholder usernames from the docs
    BLOCKED_USERNAMES = {"sherlockholmes", "example", "test", "yourusername", "your-username"}
    if username in BLOCKED_USERNAMES:
        return False, f"'{username}' is an example agent from the docs. Please submit your own agent link."

    if username in seen_usernames:
        return False, f"Duplicate link. Username '{username}' has already been submitted."

    # Check if the agent actually exists via the asi1.ai API
    api_url = f"https://asi1.ai/p/platform/v2/public/agents/shared_agent/{username}"
    try:
        resp = requests.get(api_url, timeout=10, headers={"Accept": "application/json"})
        if resp.status_code == 404:
            return False, f"Agent '{username}' does not exist on asi1.ai."
        if resp.status_code != 200:
            return False, f"Could not verify agent. API returned status {resp.status_code}."
    except requests.RequestException as e:
        return False, f"Could not reach asi1.ai to verify link: {e}"

    seen_usernames.add(username)
    _save_seen(seen_usernames)
    return True, f"Valid link. Username: '{username}'"


# --- Quick test ---
if __name__ == "__main__":
    # Reset seen for clean test run
    seen_usernames.clear()
    if os.path.exists(SEEN_FILE):
        os.remove(SEEN_FILE)

    test_links = [
        "https://asi1.ai/ai/sherlockholmes",           # valid
        "https://asi1.ai/ai/SherlockHolmes",            # duplicate (case-insensitive)
        "https://asi1.ai/ai/sherlockholmes",            # duplicate
        "https://asi1.ai/ai/sherlockholmes997",         # invalid (404 - does not exist)
        "https://asi1.ai/ai/sherlockholmes/",           # valid (trailing slash)
        "https://asi1.ai/ai/sherlockholmes?ref=abc",    # duplicate (query params stripped)
        "http://asi1.ai/ai/sherlockholmes",             # duplicate (http instead of https)
        "https://asi1.ai/ai/",                          # invalid (no username)
        "https://asi1.ai/sherlockholmes",                # invalid (missing /ai/)
        "https://google.com/ai/sherlockholmes",          # invalid (wrong domain)
        "https://asi1.ai/ai/sherlock/holmes",             # invalid (extra path)
        "not a url at all",                               # invalid
    ]

    for link in test_links:
        valid, msg = validate_link(link)
        print(f"{'✓' if valid else '✗'}  {link}\n   → {msg}\n")
