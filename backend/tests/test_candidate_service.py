"""Unit Test Suite for VERIDEX Phase 5 (Candidate Discovery, Filtering, and Ranking).

Test Coverage Required:
1. Duplicate URLs deduplication
2. Missing image filtering
3. Invalid URL filtering
4. Social source classification
5. Ordinary web source classification
6. Empty search result handling
7. Candidate scoring and ranking order
"""

import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.models.candidate_schemas import DiscoveredCandidate, CandidateDiscoveryResponse
from app.services.candidate_service import (
    normalize_candidates,
    filter_candidates,
    deduplicate_candidates,
    rank_candidates,
    discover_and_rank_candidates,
    classify_source_type,
    generate_candidate_id,
)


def test_duplicate_urls_deduplication():
    """Verify that duplicate candidate URLs are deduplicated, preserving exact/higher quality matches."""
    raw = [
        {
            "url": "https://www.instagram.com/p/C12345/",
            "title": "Instagram Post Visual Match",
            "match_type": "visual",
            "image_url": "https://cdn.example.com/img1.jpg",
            "rank": 2,
        },
        {
            "url": "https://www.instagram.com/p/C12345/",
            "title": "Instagram Post Exact Match",
            "match_type": "exact",
            "image_url": "https://cdn.example.com/img1_hd.jpg",
            "rank": 1,
        },
    ]

    normalized = normalize_candidates(raw)
    filtered = filter_candidates(normalized)
    deduped = deduplicate_candidates(filtered)

    assert len(deduped) == 1
    assert deduped[0].url == "https://www.instagram.com/p/C12345/"
    assert deduped[0].match_type == "exact"


def test_missing_image_filtering():
    """Verify that candidates lacking both image_url and thumbnail_url are filtered out."""
    raw = [
        {
            "url": "https://example.com/page1",
            "title": "Candidate with Image Asset",
            "image_url": "https://example.com/img1.jpg",
        },
        {
            "url": "https://example.com/page2",
            "title": "Candidate Missing All Images",
            "image_url": None,
            "thumbnail_url": None,
        },
        {
            "url": "https://example.com/page3",
            "title": "Candidate with Thumbnail",
            "thumbnail_url": "https://example.com/thumb.jpg",
        },
    ]

    normalized = normalize_candidates(raw)
    filtered = filter_candidates(normalized)

    assert len(filtered) == 2
    urls = [c.url for c in filtered]
    assert "https://example.com/page1" in urls
    assert "https://example.com/page3" in urls
    assert "https://example.com/page2" not in urls


def test_invalid_url_filtering():
    """Verify that candidates with invalid or non-HTTP/HTTPS URLs are filtered out."""
    raw = [
        {
            "url": "https://valid-site.org/article",
            "title": "Valid Web Candidate",
            "image_url": "https://valid-site.org/img.jpg",
        },
        {
            "url": "not_a_valid_url_string",
            "title": "Invalid String Candidate",
            "image_url": "https://valid-site.org/img.jpg",
        },
        {
            "url": "ftp://fileserver.com/image.jpg",
            "title": "FTP Scheme Candidate",
            "image_url": "https://valid-site.org/img.jpg",
        },
        {
            "url": "",
            "title": "Empty URL Candidate",
            "image_url": "https://valid-site.org/img.jpg",
        },
    ]

    normalized = normalize_candidates(raw)
    filtered = filter_candidates(normalized)

    assert len(filtered) == 1
    assert filtered[0].url == "https://valid-site.org/article"


def test_social_source_classification():
    """Verify public social media platforms are classified as source_type='social'."""
    assert classify_source_type("Instagram", "https://instagram.com/p/123") == "social"
    assert classify_source_type("X/Twitter", "https://x.com/user/123") == "social"
    assert classify_source_type("Reddit", "https://reddit.com/r/pics") == "social"
    assert classify_source_type("LinkedIn", "https://linkedin.com/in/user") == "social"
    assert classify_source_type("TikTok", "https://tiktok.com/@user") == "social"


def test_ordinary_web_source_classification():
    """Verify standard web articles and news sites are classified as source_type='web'."""
    assert classify_source_type("Web", "https://en.wikipedia.org/wiki/Lena") == "web"
    assert classify_source_type("Web", "https://news.bbc.co.uk/article1") == "web"
    assert classify_source_type("Web", "https://blog.tech.com/post") == "web"


def test_empty_search_result_handling():
    """Verify empty input search results are handled gracefully without crashing."""
    response = discover_and_rank_candidates([])

    assert isinstance(response, CandidateDiscoveryResponse)
    assert response.total_raw_candidates == 0
    assert response.filtered_candidates_count == 0
    assert response.social_candidates_count == 0
    assert response.web_candidates_count == 0
    assert response.candidates == []
    assert response.error is None


def test_candidate_scoring_and_ranking_order():
    """Verify candidate scoring algorithm prioritizes exact match social candidates."""
    raw = [
        {
            "url": "https://general-blog.com/news",
            "title": "General Web Visual Match",
            "match_type": "visual",
            "platform": "Web",
            "image_url": "https://general-blog.com/img.jpg",
            "rank": 1,
        },
        {
            "url": "https://www.instagram.com/p/evidence_post/",
            "title": "Instagram Exact Match Post",
            "match_type": "exact",
            "platform": "Instagram",
            "image_url": "https://instagram.cdn.com/img.jpg",
            "rank": 2,
        },
    ]

    res = discover_and_rank_candidates(raw)
    assert res.filtered_candidates_count == 2

    # Instagram exact match should rank #1 due to exact match (+50) + social bonus (+30)
    top = res.candidates[0]
    second = res.candidates[1]

    assert top.rank == 1
    assert top.url == "https://www.instagram.com/p/evidence_post/"
    assert top.source_type == "social"
    assert top.match_type == "exact"
    assert top.candidate_id.startswith("cand_")

    assert second.rank == 2
    assert second.url == "https://general-blog.com/news"
    assert second.source_type == "web"
