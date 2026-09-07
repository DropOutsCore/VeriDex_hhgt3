"""Google Lens Reverse Image Search Service powered by SerpApi.

==================================================
EDUCATIONAL OVERVIEW & DESIGN PRINCIPLES
==================================================

1. GENUINE REVERSE SEARCH:
   - This service interacts directly with external reverse search APIs (SerpApi Google Lens engine).
   - IT DOES NOT USE HARDCODED DEMO URLS OR FAKE CANDIDATE RESPONSES.
   - Results originate dynamically from live search engine indexes.

2. ARCHITECTURE PIPELINE:
   Input Image (Local Bytes / URL)
   ├──► Image Upload / URL Resolution (SerpApi Upload Endpoint)
   ├──► SerpApi Google Lens API Query (engine="google_lens")
   ├──► Raw JSON Parsing (exact_matches & visual_matches arrays)
   ├──► Platform Classification (Instagram, X/Twitter, LinkedIn, Reddit, Web)
   └──► Result Normalization & Ranking

3. SOCIAL MEDIA & PUBLIC PLATFORM INDEXING:
   - Identifies candidate web pages originating from publicly indexed social platforms.
   - Respects public web indexing boundaries (does NOT attempt to scrape private accounts).

4. LOGGING SECURITY:
   - All search queries, HTTP status codes, result counts, and candidate URLs are logged.
   - API KEYS ARE NEVER LOGGED IN PLAINTEXT (masked as SERPAPI_API_KEY=***).
"""

import logging
import os
from typing import List, Dict, Any, Union, Optional
from urllib.parse import urlparse
import httpx

from app.config import SERPAPI_API_KEY, SERPAPI_BASE_URL, SERPAPI_UPLOAD_URL
from app.models.lens_schemas import (
    NormalizedCandidateResult,
    LensSearchResponse,
)

# Configure logger for lens service
logger = logging.getLogger("veridex.lens_service")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def identify_platform(url: str, source: str = "") -> str:
    """Identify the source platform of a discovered candidate URL based on domain matching.

    Args:
        url: Candidate page URL.
        source: Source domain string returned by search engine.

    Returns:
        Platform category string (e.g. 'Instagram', 'X/Twitter', 'Facebook', 'LinkedIn', 'Reddit', 'TikTok', 'YouTube', 'Pinterest', 'Web').
    """
    domain = ""
    if url:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
        except Exception:
            domain = ""
    if not domain and source:
        domain = source.lower()

    if "instagram.com" in domain:
        return "Instagram"
    elif "twitter.com" in domain or "x.com" in domain:
        return "X/Twitter"
    elif "facebook.com" in domain or "fb.com" in domain:
        return "Facebook"
    elif "linkedin.com" in domain:
        return "LinkedIn"
    elif "reddit.com" in domain:
        return "Reddit"
    elif "tiktok.com" in domain:
        return "TikTok"
    elif "youtube.com" in domain or "youtu.be" in domain:
        return "YouTube"
    elif "pinterest.com" in domain:
        return "Pinterest"

    return "Web"


def upload_image_for_search(
    image_bytes: bytes,
    filename: str = "evidence.jpg",
    api_key: Optional[str] = None,
) -> str:
    """Upload local image binary bytes to SerpApi temporary image upload endpoint to obtain a public URL.

    Args:
        image_bytes: Raw binary image payload.
        filename: Filename hint for multipart upload.
        api_key: Optional SerpApi key override.

    Returns:
        Temporary public image URL string returned by SerpApi.

    Raises:
        ValueError: If API key is unconfigured or bytes payload is empty.
        RuntimeError: If SerpApi image upload fails.
    """
    key = api_key or SERPAPI_API_KEY
    if not key:
        raise ValueError("SERPAPI_API_KEY environment variable is not configured.")
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Cannot upload empty image bytes (0 length).")

    logger.info("Starting SerpApi image upload | File size: %d bytes", len(image_bytes))

    try:
        with httpx.Client(timeout=30.0) as client:
            files = {"file": (filename, image_bytes, "image/jpeg")}
            params = {"api_key": key}
            response = client.post(SERPAPI_UPLOAD_URL, params=params, files=files)

        if response.status_code != 200:
            logger.error("SerpApi upload failed | Status: %d | Body: %s", response.status_code, response.text[:200])
            raise RuntimeError(f"SerpApi image upload failed with status {response.status_code}: {response.text[:200]}")

        data = response.json()
        image_url = data.get("image_url") or data.get("url")
        if not image_url:
            raise RuntimeError(f"SerpApi upload response missing 'image_url' field: {data}")

        logger.info("SerpApi image upload successful | Temporary URL: %s", image_url)
        return image_url

    except Exception as e:
        logger.error("Error during image upload for reverse search: %s", str(e))
        raise RuntimeError(f"Failed to upload image for reverse search: {str(e)}") from e


def search_google_lens(
    image_input: Union[str, bytes],
    api_key: Optional[str] = None,
    timeout_seconds: float = 30.0,
) -> Dict[str, Any]:
    """Execute live Google Lens reverse search via SerpApi.

    Args:
        image_input: Public image URL string OR raw binary image bytes.
        api_key: Optional SerpApi API key override.
        timeout_seconds: HTTP client request timeout in seconds.

    Returns:
        Raw JSON response dict from SerpApi.

    Raises:
        ValueError: If API key is missing or input is invalid.
        RuntimeError: If API call fails or times out.
    """
    key = api_key or SERPAPI_API_KEY
    if not key:
        logger.error("SerpApi search failed: SERPAPI_API_KEY environment variable is not configured.")
        raise ValueError("SERPAPI_API_KEY environment variable is not configured. Set SERPAPI_API_KEY in .env file.")

    image_url: str = ""
    if isinstance(image_input, bytes):
        image_url = upload_image_for_search(image_input, api_key=key)
    elif isinstance(image_input, str):
        if image_input.startswith(("http://", "https://")):
            image_url = image_input
        else:
            raise ValueError(f"Invalid image URL format: '{image_input}'. Must start with http:// or https://")
    else:
        raise ValueError(f"Unsupported image input type for search: {type(image_input).__name__}")

    masked_key = f"{key[:4]}***{key[-4:]}" if len(key) >= 8 else "***"
    logger.info("Search started | Engine: Google Lens | Query URL: %s | API Key: %s", image_url, masked_key)

    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": key,
    }

    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.get(SERPAPI_BASE_URL, params=params)

        if response.status_code == 401:
            logger.error("SerpApi authentication failed (HTTP 401). Invalid API key.")
            raise RuntimeError("SerpApi authentication failed: Invalid or unauthorized API key.")
        elif response.status_code == 429:
            logger.error("SerpApi rate limit exceeded (HTTP 429).")
            raise RuntimeError("SerpApi rate limit exceeded. Please check plan quota.")
        elif response.status_code != 200:
            logger.error("SerpApi request failed | HTTP %d | Body: %s", response.status_code, response.text[:200])
            raise RuntimeError(f"SerpApi Google Lens query failed with status {response.status_code}: {response.text[:200]}")

        raw_data = response.json()
        logger.info("Search completed successfully | HTTP 200")
        return raw_data

    except httpx.TimeoutException as e:
        logger.error("SerpApi request timed out after %.1f seconds", timeout_seconds)
        raise RuntimeError(f"Google Lens search timed out after {timeout_seconds}s") from e
    except Exception as e:
        if isinstance(e, RuntimeError) or isinstance(e, ValueError):
            raise
        logger.error("Network or execution error during Google Lens search: %s", str(e))
        raise RuntimeError(f"Google Lens search error: {str(e)}") from e


def get_exact_matches(raw_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract exact image match results from raw SerpApi Google Lens payload.

    Args:
        raw_results: SerpApi JSON dictionary response.

    Returns:
        List of exact match candidate dictionary objects.
    """
    if not isinstance(raw_results, dict):
        return []

    exact_matches: List[Dict[str, Any]] = []

    # 1. SerpApi 'exact_matches' key
    if "exact_matches" in raw_results and isinstance(raw_results["exact_matches"], list):
        exact_matches.extend(raw_results["exact_matches"])

    # 2. Key 'visual_matches' with high relevance or exact tag
    if "visual_matches" in raw_results and isinstance(raw_results["visual_matches"], list):
        for item in raw_results["visual_matches"]:
            if item.get("match_type") == "exact" or item.get("relevance") == "exact":
                if item not in exact_matches:
                    exact_matches.append(item)

    return exact_matches


def get_visual_matches(raw_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract visual match results from raw SerpApi Google Lens payload.

    Args:
        raw_results: SerpApi JSON dictionary response.

    Returns:
        List of visual match candidate dictionary objects.
    """
    if not isinstance(raw_results, dict):
        return []

    visual_matches: List[Dict[str, Any]] = []
    if "visual_matches" in raw_results and isinstance(raw_results["visual_matches"], list):
        visual_matches.extend(raw_results["visual_matches"])

    return visual_matches


def normalize_search_results(raw_results: Dict[str, Any]) -> List[NormalizedCandidateResult]:
    """Convert raw SerpApi Google Lens JSON into normalized candidate records.

    Handles field fallbacks gracefully for missing API response keys.

    Args:
        raw_results: SerpApi JSON payload.

    Returns:
        Ordered list of NormalizedCandidateResult Pydantic objects.
    """
    normalized: List[NormalizedCandidateResult] = []
    seen_urls = set()

    exact_matches = get_exact_matches(raw_results)
    visual_matches = get_visual_matches(raw_results)

    rank_counter = 1

    # 1. Process Exact Matches first
    for item in exact_matches:
        url = item.get("link") or item.get("url") or item.get("page_url") or ""
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = item.get("title") or item.get("snippet") or "Untitled Image Match"
        source = item.get("source") or item.get("domain") or urlparse(url).netloc or "Unknown Source"
        image_url = item.get("image") or item.get("original") or item.get("image_url") or None
        thumbnail_url = item.get("thumbnail") or item.get("thumbnail_url") or None
        platform = identify_platform(url, source=source)

        normalized.append(
            NormalizedCandidateResult(
                rank=rank_counter,
                title=title,
                source=source,
                url=url,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                match_type="exact",
                platform=platform,
            )
        )
        rank_counter += 1

    # 2. Process Visual Matches (Fallback / Complementary discovery)
    for item in visual_matches:
        url = item.get("link") or item.get("url") or item.get("page_url") or ""
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = item.get("title") or item.get("snippet") or "Visual Image Match"
        source = item.get("source") or item.get("domain") or urlparse(url).netloc or "Unknown Source"
        image_url = item.get("image") or item.get("original") or item.get("image_url") or None
        thumbnail_url = item.get("thumbnail") or item.get("thumbnail_url") or None
        platform = identify_platform(url, source=source)

        normalized.append(
            NormalizedCandidateResult(
                rank=rank_counter,
                title=title,
                source=source,
                url=url,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                match_type="visual",
                platform=platform,
            )
        )
        rank_counter += 1

    logger.info("Normalized search results | Total candidates: %d (Exact: %d, Visual: %d)",
                len(normalized), len(exact_matches), len(visual_matches))
    if normalized:
        candidate_urls = [c.url for c in normalized[:5]]
        logger.info("Top Candidate URLs Discovered: %s", candidate_urls)

    return normalized


def execute_lens_search_pipeline(
    image_input: Union[str, bytes],
    api_key: Optional[str] = None,
) -> LensSearchResponse:
    """Execute end-to-end Google Lens reverse image search pipeline.

    Args:
        image_input: Public image URL or raw image binary bytes.
        api_key: Optional SerpApi key override.

    Returns:
        LensSearchResponse schema.
    """
    key = api_key or SERPAPI_API_KEY
    if not key:
        return LensSearchResponse(
            search_executed=False,
            total_results_found=0,
            error="SERPAPI_API_KEY environment variable is not configured. Please set SERPAPI_API_KEY in your .env file.",
        )

    try:
        raw_results = search_google_lens(image_input, api_key=key)
        candidates = normalize_search_results(raw_results)

        exact_count = sum(1 for c in candidates if c.match_type == "exact")
        visual_count = sum(1 for c in candidates if c.match_type == "visual")

        query_url = raw_results.get("search_metadata", {}).get("google_lens_url") or (image_input if isinstance(image_input, str) else "Uploaded Image Bytes")

        return LensSearchResponse(
            search_executed=True,
            query_image_url=query_url,
            total_results_found=len(candidates),
            exact_matches_count=exact_count,
            visual_matches_count=visual_count,
            candidates=candidates,
        )

    except Exception as e:
        logger.error("Reverse image search pipeline error: %s", str(e))
        return LensSearchResponse(
            search_executed=False,
            total_results_found=0,
            error=str(e),
        )
