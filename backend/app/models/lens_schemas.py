"""Pydantic schemas for Google Lens reverse image search and normalized candidates."""

from typing import List, Optional
from pydantic import BaseModel, Field


class NormalizedCandidateResult(BaseModel):
    """Normalized web candidate discovered via Google Lens reverse search."""
    rank: int = Field(..., ge=1, description="Numerical ranking of the search candidate")
    title: str = Field(..., description="Page title or description of discovered content")
    source: str = Field(..., description="Domain name or publisher source (e.g. instagram.com, wikipedia.org)")
    url: str = Field(..., description="Canonical web URL of candidate page")
    image_url: Optional[str] = Field(None, description="Direct URL of candidate image asset")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail preview URL returned by search engine")
    match_type: str = Field("visual", description="Match type classification ('exact' or 'visual')")
    platform: str = Field("Web", description="Platform identification (e.g. Instagram, X/Twitter, Reddit, Web)")


class LensSearchResponse(BaseModel):
    """Structured output for reverse image search queries."""
    search_executed: bool = Field(..., description="True if external search request succeeded")
    query_image_url: Optional[str] = Field(None, description="URL of query image sent to search engine")
    total_results_found: int = Field(0, ge=0, description="Total normalized candidates returned")
    exact_matches_count: int = Field(0, ge=0, description="Count of exact matches")
    visual_matches_count: int = Field(0, ge=0, description="Count of visual matches")
    candidates: List[NormalizedCandidateResult] = Field(default_factory=list, description="List of normalized candidates")
    search_engine: str = Field("SerpApi / Google Lens", description="Search engine engine tag")
    error: Optional[str] = Field(None, description="Error message if search failed or API key was missing")
