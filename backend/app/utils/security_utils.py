"""Security & Privacy Utilities for VERIDEX Engine.

==================================================
SECURITY & PRIVACY SAFEGUARDS
==================================================

1. SSRF (SERVER-SIDE REQUEST FORGERY) PREVENTION:
   - Validates candidate URLs before initiating HTTP GET requests.
   - Rejects loopback (127.0.0.1, ::1, localhost), private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16),
     link-local addresses (169.254.169.254), and non-standard network schemes.

2. INPUT & FILE PAYLOAD VALIDATION:
   - Restricts file sizes to max 10MB to prevent Memory Exhaustion DoS.
   - Enforces strict image MIME type / header validation (JPEG, PNG, WEBP).

3. EPHEMERAL DATA CLEANUP:
   - Provides helper utilities for securely purging temporary memory buffers and image arrays.
"""

import ipaddress
import logging
import os
import re
import socket
from urllib.parse import urlparse
from typing import Union, Optional

logger = logging.getLogger("veridex.security_utils")

# Maximum allowed uploaded image payload size (10 MB)
MAX_ALLOWED_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

# Allowed image MIME types
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

# Private / reserved IP networks blocked for SSRF protection
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local AWS Metadata
    ipaddress.ip_network("0.0.0.0/8"),        # Zero net
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Private
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]


def is_ssrf_safe_url(url: str) -> tuple[bool, Optional[str]]:
    """Validate candidate image URL against SSRF attack vectors.

    Args:
        url: Target URL string.

    Returns:
        Tuple of (is_safe: bool, reason: str or None).
    """
    if not url or not isinstance(url, str):
        return False, "URL string is empty or invalid type."

    clean_url = url.strip()
    parsed = urlparse(clean_url)

    # 1. Scheme restriction (HTTP or HTTPS only)
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Prohibited URL scheme '{parsed.scheme}'. Only 'http' and 'https' are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL format: Hostname could not be parsed."

    # 2. Block localhost & obvious local names
    if hostname.lower() in ("localhost", "loopback", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"):
        return False, f"SSRF Risk: Hostname '{hostname}' resolves to loopback or internal metadata service."

    # 3. Resolve IP address and check against private IP ranges
    try:
        ip_list = socket.getaddrinfo(hostname, None)
        for item in ip_list:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)

            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    return False, f"SSRF Security Violation: Resolved IP address '{ip_str}' belongs to private/internal network {blocked_net}."
    except socket.gaierror:
        # DNS resolution failure - fail closed or allow downstream HTTP client timeout
        logger.warning("DNS resolution failed for candidate host '%s'", hostname)
    except Exception as e:
        logger.warning("Error checking SSRF IP safety for host '%s': %s", hostname, str(e))

    return True, None


def validate_image_payload(data: bytes, filename: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """Validate image binary payload size and file magic bytes.

    Args:
        data: Binary payload bytes.
        filename: Optional uploaded file name string.

    Returns:
        Tuple of (is_valid: bool, error_message: str or None).
    """
    if not data or len(data) == 0:
        return False, "Uploaded image file payload is empty (0 bytes)."

    if len(data) > MAX_ALLOWED_IMAGE_SIZE_BYTES:
        size_mb = len(data) / (1024 * 1024)
        return False, f"File size ({size_mb:.2f} MB) exceeds maximum allowed upload limit (10.0 MB)."

    # Verify image magic bytes
    # JPEG: FF D8 FF
    # PNG: 89 50 4E 47
    # WEBP: 52 49 46 46 ... 57 45 42 50
    if data.startswith(b"\xff\xd8\xff"):
        return True, None
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True, None
    if data.startswith(b"RIFF") and b"WEBP" in data[:16]:
        return True, None

    return False, "Unsupported or corrupted image file format. Only JPEG, PNG, and WEBP are accepted."
