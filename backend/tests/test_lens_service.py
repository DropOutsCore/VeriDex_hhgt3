"""Unit, Mock, and Integration Test Suite for VERIDEX Phase 4 (Google Lens Reverse Image Search).

Categorized Test Coverage:
1. Unit Tests:
   - Social media & public platform domain identification
   - Raw SerpApi exact & visual matches extraction
   - Normalized result schema conversion with missing field fallbacks
2. Mock API Tests:
   - Missing API key error handling
   - Invalid query image input validation
   - Mocked SerpApi HTTP 200 successful payload parsing
   - Mocked SerpApi HTTP 429 rate limit error handling
   - Mocked SerpApi HTTP 401 unauthorized error handling
   - Mocked SerpApi HTTP timeout handling
3. Real Integration Test:
   - Live integration test executed ONLY when SERPAPI_API_KEY is present in environment.
"""

import os
import sys
from unittest.mock import patch, MagicMock
import pytest
import httpx
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.config import SERPAPI_API_KEY
from app.services.lens_service import (
    identify_platform,
    get_exact_matches,
    get_visual_matches,
    normalize_search_results,
    search_google_lens,
    execute_lens_search_pipeline,
)
from app.models.lens_schemas import LensSearchResponse, NormalizedCandidateResult

client = TestClient(app)


# -------------------------------------------------------------------
# 1. Unit Tests (Parsers & Platform Classifiers)
# -------------------------------------------------------------------

def test_identify_platform_domains():
    """Verify social media and web platform identification from URLs and sources."""
    assert identify_platform("https://www.instagram.com/p/C12345/") == "Instagram"
    assert identify_platform("https://twitter.com/user/status/123") == "X/Twitter"
    assert identify_platform("https://x.com/user/status/123") == "X/Twitter"
    assert identify_platform("https://www.facebook.com/photo.php") == "Facebook"
    assert identify_platform("https://www.linkedin.com/in/profile") == "LinkedIn"
    assert identify_platform("https://www.reddit.com/r/technology/comments/123") == "Reddit"
    assert identify_platform("https://www.tiktok.com/@user/video/123") == "TikTok"
    assert identify_platform("https://www.youtube.com/watch?v=123") == "YouTube"
    assert identify_platform("https://www.pinterest.com/pin/123") == "Pinterest"
    assert identify_platform("https://en.wikipedia.org/wiki/Lena") == "Web"


def test_get_exact_and_visual_matches_extraction():
    """Verify extraction of exact matches and visual matches from raw payload."""
    raw_payload = {
        "exact_matches": [
            {"title": "Exact Match 1", "link": "https://example.com/exact1"}
        ],
        "visual_matches": [
            {"title": "Visual Match 1", "link": "https://example.com/vis1"},
            {"title": "Visual Match 2", "link": "https://instagram.com/p/xyz", "match_type": "exact"}
        ]
    }

    exacts = get_exact_matches(raw_payload)
    visuals = get_visual_matches(raw_payload)

    assert len(exacts) == 2  # 1 from exact_matches array + 1 tagged match_type="exact"
    assert len(visuals) == 2


def test_normalize_search_results():
    """Verify normalization of raw SerpApi results into NormalizedCandidateResult objects."""
    raw_payload = {
        "visual_matches": [
            {
                "title": "Sample Candidate Match",
                "source": "Reddit",
                "link": "https://www.reddit.com/r/pics/comments/sample",
                "original": "https://i.redd.it/sample.jpg",
                "thumbnail": "https://thumb.redd.it/sample.jpg"
            }
        ]
    }

    normalized = normalize_search_results(raw_payload)
    assert len(normalized) == 1

    candidate = normalized[0]
    assert isinstance(candidate, NormalizedCandidateResult)
    assert candidate.rank == 1
    assert candidate.title == "Sample Candidate Match"
    assert candidate.platform == "Reddit"
    assert candidate.url == "https://www.reddit.com/r/pics/comments/sample"
    assert candidate.image_url == "https://i.redd.it/sample.jpg"
    assert candidate.thumbnail_url == "https://thumb.redd.it/sample.jpg"


def test_normalize_search_results_missing_fields_fallback():
    """Verify field fallback handling when raw response keys are missing."""
    raw_payload = {
        "visual_matches": [
            {
                "link": "https://subdomain.example.com/page",
                # Title, source, image, thumbnail missing
            }
        ]
    }

    normalized = normalize_search_results(raw_payload)
    assert len(normalized) == 1
    c = normalized[0]
    assert c.title == "Visual Image Match"
    assert c.source == "subdomain.example.com"
    assert c.platform == "Web"


# -------------------------------------------------------------------
# 2. Mock API Tests (HTTP Errors, Rate Limits, Missing Keys)
# -------------------------------------------------------------------

def test_search_google_lens_missing_api_key():
    """Verify ValueError is raised when API key is missing."""
    with pytest.raises(ValueError, match="SERPAPI_API_KEY environment variable is not configured"):
        search_google_lens("https://example.com/image.jpg", api_key="")


def test_search_google_lens_invalid_input():
    """Verify ValueError for non-HTTP query strings."""
    with pytest.raises(ValueError, match="Invalid image URL format"):
        search_google_lens("invalid_url_string", api_key="test_key")


@patch("httpx.Client.get")
def test_search_google_lens_mock_success(mock_get):
    """Verify parsing of mocked SerpApi HTTP 200 response."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "search_metadata": {"status": "Success"},
        "visual_matches": [
            {
                "title": "Mock Candidate Image",
                "source": "Instagram",
                "link": "https://www.instagram.com/p/mock_post/",
                "thumbnail": "https://thumbnail.example.com/1.jpg"
            }
        ]
    }
    mock_get.return_value = mock_resp

    response = search_google_lens("https://example.com/query.jpg", api_key="dummy_key_12345")
    assert "visual_matches" in response
    assert len(response["visual_matches"]) == 1
    assert response["visual_matches"][0]["title"] == "Mock Candidate Image"


@patch("httpx.Client.get")
def test_search_google_lens_mock_rate_limit(mock_get):
    """Verify rate limit HTTP 429 error handling."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"
    mock_get.return_value = mock_resp

    with pytest.raises(RuntimeError, match="SerpApi rate limit exceeded"):
        search_google_lens("https://example.com/query.jpg", api_key="dummy_key_12345")


@patch("httpx.Client.get")
def test_search_google_lens_mock_unauthorized(mock_get):
    """Verify HTTP 401 unauthorized error handling."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Invalid API key"
    mock_get.return_value = mock_resp

    with pytest.raises(RuntimeError, match="SerpApi authentication failed"):
        search_google_lens("https://example.com/query.jpg", api_key="invalid_key")


@patch("httpx.Client.get")
def test_search_google_lens_mock_timeout(mock_get):
    """Verify HTTP timeout error handling."""
    mock_get.side_effect = httpx.TimeoutException("Connection timed out")

    with pytest.raises(RuntimeError, match="search timed out"):
        search_google_lens("https://example.com/query.jpg", api_key="dummy_key")


def test_api_search_endpoint_missing_params():
    """Verify POST /api/search returns 400 when neither file nor image_url is provided."""
    response = client.post("/api/search")
    assert response.status_code == 400
    assert "Must provide either" in response.json()["detail"]


# -------------------------------------------------------------------
# 3. Real Integration Test (Executes Live Search ONLY when SERPAPI_API_KEY exists)
# -------------------------------------------------------------------

@pytest.mark.integration
def test_real_google_lens_integration():
    """Live integration test querying SerpApi Google Lens.

    Only executes when SERPAPI_API_KEY is configured in environment / .env.
    NEVER fakes success — verifies actual non-hardcoded candidate responses.
    """
    key = SERPAPI_API_KEY or os.getenv("SERPAPI_API_KEY", "")
    if not key:
        pytest.skip("SERPAPI_API_KEY not configured in environment. Skipping live integration test.")

    test_image_url = "https://raw.githubusercontent.com/opencv/opencv/4.x/samples/data/lena.jpg"
    response = execute_lens_search_pipeline(test_image_url, api_key=key)

    assert isinstance(response, LensSearchResponse)
    assert response.search_executed is True
    assert response.error is None
    assert response.total_results_found > 0
    assert len(response.candidates) > 0

    top_candidate = response.candidates[0]
    assert isinstance(top_candidate, NormalizedCandidateResult)
    assert top_candidate.rank == 1
    assert len(top_candidate.url) > 0
    assert len(top_candidate.title) > 0
    assert len(top_candidate.source) > 0
    assert top_candidate.platform in ["Web", "Instagram", "X/Twitter", "Facebook", "LinkedIn", "Reddit", "TikTok", "YouTube", "Pinterest"]
