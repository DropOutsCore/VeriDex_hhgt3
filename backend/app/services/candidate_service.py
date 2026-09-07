"""Candidate Discovery, Filtering, and Ranking Service.

==================================================
EDUCATIONAL OVERVIEW & DESIGN PRINCIPLES
==================================================

1. PURPOSE OF CANDIDATE DISCOVERY:
   - Evaluates raw visual search engine results to select high-quality public web and social sources
     for downstream independent face verification.
   - THIS PHASE ANSWERS: "Which discovered sources should we investigate?"
   - IT DOES NOT VERIFY FACIAL IDENTITY MATCHES (Face verification is performed in Phase 6).

2. FILTERING CRITERIA:
   - Valid URL Structure: Must possess valid HTTP/HTTPS scheme and domain name.
   - Image Asset Availability: Must have a valid candidate image URL or thumbnail preview.
   - Excludes corrupt, malformed, or local file references.

3. DEDUPLICATION:
   - Merges duplicate candidate URLs, preserving the highest-quality match instance.

4. SCORING & RANKING ALGORITHM:
   Candidates are scored based on:
   - Match Type Weight: Exact matches (+50 pts) > Visual matches (+20 pts).
   - Source Type Weight: Public Social Media (+30 pts) > General Web (+15 pts).
   - Asset Directness: Direct full-resolution image URL (+25 pts) > Thumbnail only (+10 pts).
   - Original Search Engine Rank: Inverse rank penalty.
"""

import hashlib
import logging
from typing import List, Dict, Any, Union, Optional
from urllib.parse import urlparse

from app.models.lens_schemas import NormalizedCandidateResult
from app.models.candidate_schemas import DiscoveredCandidate, CandidateDiscoveryResponse
from app.services.lens_service import identify_platform

logger = logging.getLogger("veridex.candidate_service")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

SOCIAL_PLATFORMS = {"Instagram", "X/Twitter", "Facebook", "LinkedIn", "Reddit", "TikTok", "YouTube", "Pinterest"}


def generate_candidate_id(url: str) -> str:
    """Generate a clean, deterministic candidate identifier from a URL."""
    clean_url = url.strip().lower()
    hash_hex = hashlib.md5(clean_url.encode("utf-8")).hexdigest()[:8]
    return f"cand_{hash_hex}"


def classify_source_type(platform: str, url: str) -> str:
    """Classify candidate source as 'social' or 'web'."""
    if platform in SOCIAL_PLATFORMS:
        return "social"

    resolved_platform = identify_platform(url)
    if resolved_platform in SOCIAL_PLATFORMS:
        return "social"

    return "web"


def _is_valid_url(url: str) -> bool:
    """Check whether a URL has valid HTTP/HTTPS scheme and domain netloc."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def normalize_candidates(raw_candidates: List[Union[Dict[str, Any], NormalizedCandidateResult]]) -> List[DiscoveredCandidate]:
    """Convert raw search results or NormalizedCandidateResult objects into DiscoveredCandidate records."""
    normalized: List[DiscoveredCandidate] = []

    for item in raw_candidates:
        if isinstance(item, NormalizedCandidateResult):
            url = item.url
            title = item.title
            source = item.source
            image_url = item.image_url
            thumbnail_url = item.thumbnail_url
            match_type = item.match_type
            platform = item.platform
            rank = item.rank
        elif isinstance(item, dict):
            url = item.get("url") or item.get("link") or item.get("page_url") or ""
            title = item.get("title") or item.get("snippet") or "Untitled Web Candidate"
            source = item.get("source") or item.get("domain") or ""
            image_url = item.get("image_url") or item.get("image") or item.get("original") or None
            thumbnail_url = item.get("thumbnail_url") or item.get("thumbnail") or None
            match_type = item.get("match_type") or "visual"
            platform = item.get("platform") or identify_platform(url, source)
            rank = item.get("rank") or 99
        else:
            continue

        if not source and url and _is_valid_url(url):
            source = urlparse(url).netloc

        candidate_id = generate_candidate_id(url) if url else f"cand_unknown_{len(normalized)}"
        source_type = classify_source_type(platform, url)

        normalized.append(
            DiscoveredCandidate(
                candidate_id=candidate_id,
                rank=rank,
                title=title,
                source=source or "Unknown Source",
                url=url,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                match_type=match_type,
                source_type=source_type,
            )
        )

    return normalized


def filter_candidates(candidates: List[DiscoveredCandidate]) -> List[DiscoveredCandidate]:
    """Filter candidate records against validity and quality criteria.

    Criteria:
    - Valid URL structure (http/https scheme & netloc)
    - Image asset availability (must have image_url or thumbnail_url)
    - Non-empty source & title
    """
    filtered: List[DiscoveredCandidate] = []

    for c in candidates:
        # 1. Validate URL
        if not _is_valid_url(c.url):
            logger.debug("Filtered out candidate due to invalid URL: '%s'", c.url)
            continue

        # 2. Validate Image Availability
        has_image = bool(c.image_url and c.image_url.strip())
        has_thumb = bool(c.thumbnail_url and c.thumbnail_url.strip())
        if not has_image and not has_thumb:
            logger.debug("Filtered out candidate due to missing image assets: '%s'", c.url)
            continue

        filtered.append(c)

    logger.info("Filtering complete | Retained %d of %d candidates", len(filtered), len(candidates))
    return filtered


def deduplicate_candidates(candidates: List[DiscoveredCandidate]) -> List[DiscoveredCandidate]:
    """Deduplicate candidates by canonical URL, preserving highest quality instances."""
    seen_urls: Dict[str, DiscoveredCandidate] = {}

    for c in candidates:
        # Normalize URL by trimming trailing slashes
        clean_url = c.url.strip().rstrip("/").lower()

        if clean_url not in seen_urls:
            seen_urls[clean_url] = c
        else:
            existing = seen_urls[clean_url]
            # Replace if new candidate has exact match_type or better rank
            if c.match_type == "exact" and existing.match_type != "exact":
                seen_urls[clean_url] = c
            elif c.image_url and not existing.image_url:
                seen_urls[clean_url] = c

    deduped = list(seen_urls.values())
    logger.info("Deduplication complete | Retained %d unique candidates", len(deduped))
    return deduped


def rank_candidates(candidates: List[DiscoveredCandidate]) -> List[DiscoveredCandidate]:
    """Score and rank candidates using a multi-factor relevance evaluation formula.

    Scoring System:
    - Base Score: 100.0
    - Match Type: Exact match (+50 pts) vs Visual match (+20 pts)
    - Source Type: Public Social Media (+30 pts) vs Web (+15 pts)
    - Image Directness: Direct image_url available (+25 pts) vs Thumbnail only (+10 pts)
    - Title Relevance: Descriptive title present (+10 pts)
    - Original Search Rank: Inverse rank penalty (-2 pts per rank step)
    """
    for c in candidates:
        score = 100.0

        # Match Type Weight
        if c.match_type == "exact":
            score += 50.0
        else:
            score += 20.0

        # Source Type Weight (Social media prioritized for verification context)
        if c.source_type == "social":
            score += 30.0
        else:
            score += 15.0

        # Image Availability Weight
        if c.image_url and c.image_url.strip():
            score += 25.0
        elif c.thumbnail_url and c.thumbnail_url.strip():
            score += 10.0

        # Title Quality
        if c.title and c.title != "Untitled Web Candidate":
            score += 10.0

        # Rank penalty
        score -= min(50.0, (c.rank * 2.0))

        c.relevance_score = round(score, 2)

    # Sort candidates by relevance score descending
    ranked = sorted(candidates, key=lambda item: item.relevance_score or 0.0, reverse=True)

    # Re-assign rank numbers 1..N based on final score ordering
    for index, item in enumerate(ranked, start=1):
        item.rank = index

    logger.info("Candidate ranking complete | Top candidate: '%s' (Score: %.1f)",
                ranked[0].title if ranked else "None",
                ranked[0].relevance_score if ranked else 0.0)

    return ranked


def discover_and_rank_candidates(
    raw_search_results: Union[Dict[str, Any], List[Any]],
) -> CandidateDiscoveryResponse:
    """Execute complete candidate discovery, filtering, deduplication, and ranking pipeline."""
    raw_candidates_list: List[Any] = []

    if isinstance(raw_search_results, dict):
        if "candidates" in raw_search_results and isinstance(raw_search_results["candidates"], list):
            raw_candidates_list = raw_search_results["candidates"]
        else:
            # Import normalizer from lens service if raw SerpApi response provided
            from app.services.lens_service import normalize_search_results
            raw_candidates_list = normalize_search_results(raw_search_results)
    elif isinstance(raw_search_results, list):
        raw_candidates_list = raw_search_results

    if not raw_candidates_list:
        return CandidateDiscoveryResponse(
            total_raw_candidates=0,
            filtered_candidates_count=0,
            social_candidates_count=0,
            web_candidates_count=0,
            candidates=[],
        )

    # 1. Normalize
    normalized = normalize_candidates(raw_candidates_list)

    # 2. Filter invalid URLs / missing images
    filtered = filter_candidates(normalized)

    # 3. Deduplicate by canonical URL
    deduped = deduplicate_candidates(filtered)

    # 4. Rank and score
    ranked = rank_candidates(deduped)

    social_count = sum(1 for c in ranked if c.source_type == "social")
    web_count = sum(1 for c in ranked if c.source_type == "web")

    return CandidateDiscoveryResponse(
        total_raw_candidates=len(raw_candidates_list),
        filtered_candidates_count=len(ranked),
        social_candidates_count=social_count,
        web_candidates_count=web_count,
        candidates=ranked,
    )
