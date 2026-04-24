import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests

SUPPORTED_HOSTS = (
    "amazon.in",
    "amazon.com",
    "flipkart.com",
)


def _normalize_hostname(hostname: str) -> str:
    return hostname.lower().rstrip(".")


def _matches_supported_host(hostname: str) -> bool:
    normalized = _normalize_hostname(hostname)
    for supported_host in SUPPORTED_HOSTS:
        if normalized == supported_host or normalized.endswith(f".{supported_host}"):
            return True
    return False


def _validate_resolved_addresses(hostname: str, port: int) -> None:
    try:
        addresses = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("Could not resolve the product URL host.") from exc

    if not addresses:
        raise ValueError("Could not resolve the product URL host.")

    for _, _, _, _, sockaddr in addresses:
        ip_address = ipaddress.ip_address(sockaddr[0])
        if (
            ip_address.is_private
            or ip_address.is_loopback
            or ip_address.is_link_local
            or ip_address.is_multicast
            or ip_address.is_unspecified
            or ip_address.is_reserved
        ):
            raise ValueError("Product URL resolves to a non-public network address.")


def ensure_safe_product_url(url: str) -> str:
    candidate = (url or "").strip()
    parsed = urlparse(candidate)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https product URLs are supported.")

    if not parsed.netloc or not parsed.hostname:
        raise ValueError("Invalid URL format.")

    if parsed.username or parsed.password:
        raise ValueError("Credentialed URLs are not allowed.")

    if parsed.port and parsed.port not in {80, 443}:
        raise ValueError("Only standard web ports are allowed.")

    hostname = _normalize_hostname(parsed.hostname)
    if not _matches_supported_host(hostname):
        raise ValueError("Only Amazon and Flipkart product URLs are supported.")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    _validate_resolved_addresses(hostname, port)
    return candidate


def safe_get(
    url: str,
    *,
    headers: dict | None = None,
    timeout: int = 15,
    session: requests.Session | None = None,
    max_redirects: int = 5,
):
    client = session or requests.Session()
    current_url = ensure_safe_product_url(url)

    for _ in range(max_redirects + 1):
        response = client.get(
            current_url,
            headers=headers,
            timeout=timeout,
            allow_redirects=False,
        )

        if response.is_redirect or response.is_permanent_redirect:
            redirect_target = response.headers.get("location")
            if not redirect_target:
                return response
            current_url = ensure_safe_product_url(urljoin(current_url, redirect_target))
            continue

        return response

    raise requests.TooManyRedirects("Too many redirects while fetching the product URL.")