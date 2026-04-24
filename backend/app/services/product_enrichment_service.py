"""Lightweight Amazon enrichment — extract brand, category, title from a product URL.

Kept intentionally small: one HTTP fetch per product, BeautifulSoup parse,
returns a dict. Safe to call from an endpoint that handles one product at a time.
"""
from __future__ import annotations

import random
import re
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def _headers() -> dict:
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }


def _clean(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def _extract_brand(soup: BeautifulSoup) -> str:
    # 1. Product Overview table — most reliable (label/value pairs)
    po = soup.find("div", {"id": "productOverview_feature_div"})
    if po:
        for row in po.find_all("tr"):
            cells = [_clean(c.get_text()) for c in row.find_all(["td", "th"])]
            cells = [c for c in cells if c]
            if len(cells) >= 2 and cells[0].lower() == "brand":
                return cells[1]

    # 2. bylineInfo link ("Visit the X Store" / "Brand: X")
    byline = soup.find("a", {"id": "bylineInfo"})
    if byline:
        text = _clean(byline.get_text())
        # "Visit the X Store"
        m = re.match(r"Visit the\s+(.+?)\s+Store\s*$", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # "Brand: X"
        m = re.match(r"Brand:\s*(.+)$", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # "X Store" (no "Visit the" prefix)
        m = re.match(r"(.+?)\s+Store\s*$", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    # 3. detailBullets list
    db = soup.find("div", {"id": "detailBullets_feature_div"})
    if db:
        for li in db.find_all("li"):
            text = _clean(li.get_text(" "))
            m = re.match(r"(?:Manufacturer|Brand)\s*[:‏\s]+(.+)$", text, re.IGNORECASE)
            if m:
                return m.group(1).split("\u200f")[0].strip()[:100]

    return ""


def _extract_category(soup: BeautifulSoup) -> str:
    # 1. Breadcrumb at top of page
    crumbs = soup.select("#wayfinding-breadcrumbs_feature_div li a")
    parts = [_clean(a.get_text()) for a in crumbs if _clean(a.get_text())]
    if parts:
        if len(parts) == 1:
            return parts[0]
        return f"{parts[0]} > {parts[-1]}"

    # 2. Best Sellers Rank often contains category path
    for li in soup.find_all("li"):
        text = _clean(li.get_text(" "))
        if text.lower().startswith("best sellers rank"):
            # e.g. "Best Sellers Rank: #123 in Electronics (See Top 100 in Electronics) #5 in Smart Speakers"
            cats = re.findall(r"in\s+([A-Za-z][A-Za-z &']+?)(?:\s*\(|\s*#|\s*$)", text)
            cats = [c.strip() for c in cats if c.strip() and c.strip().lower() != "see top"]
            # Dedup keeping order
            seen, uniq = set(), []
            for c in cats:
                if c.lower() not in seen:
                    seen.add(c.lower()); uniq.append(c)
            if uniq:
                if len(uniq) == 1:
                    return uniq[0]
                return f"{uniq[0]} > {uniq[-1]}"

    # 3. Category meta tag
    dept = soup.find("select", {"id": "searchDropdownBox"})
    if dept:
        opt = dept.find("option", {"selected": True})
        if opt:
            v = _clean(opt.get_text())
            if v and v.lower() not in ("all", "all categories", "all departments"):
                return v

    return ""


def _extract_title(soup: BeautifulSoup) -> str:
    t = soup.find("span", {"id": "productTitle"})
    return _clean(t.get_text()) if t else ""


def enrich_amazon_product(url: str, timeout: int = 12) -> dict:
    """Fetch an Amazon product page and return {brand, category, title}.

    Returns empty strings for fields it couldn't extract. Raises on network errors.
    """
    domain = urlparse(url).netloc.lower()
    if "amazon" not in domain:
        return {"brand": "", "category": "", "title": ""}

    resp = requests.get(url, headers=_headers(), timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    return {
        "brand": _extract_brand(soup),
        "category": _extract_category(soup),
        "title": _extract_title(soup),
    }
