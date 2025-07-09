import logging

import requests

from src import constants, utils

log = logging.getLogger(__name__)
SESSION = requests.Session()


def open_issue(lang_src: str, lang_dst: str, word: str) -> str:
    """Open an issue on the tracker, and return the ticket's URL."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {constants.GITHUB_PAT}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {
        "title": f"[{lang_src.upper()}-{lang_dst.upper()}] {word}",
        "body": f"👀 [{word}](https://{lang_dst}.wiktionary.org/wiki/{word})",
        "labels": [utils.tr(lang_dst), "feedback", "triage"],
    }
    with SESSION.post(constants.GITHUB_API_TRACKER, headers=headers, json=data) as req:
        req.raise_for_status()
        return req.json()["html_url"]
