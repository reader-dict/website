from collections.abc import Generator

import responses

from src import github

from .payloads import GITHUB_ISSUE_URL


@responses.activate()
def test_open_issue(mock_responses: Generator) -> None:
    assert github.open_issue("es", "en", "soportaba") == GITHUB_ISSUE_URL
