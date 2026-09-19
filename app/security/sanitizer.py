"""
HTML Sanitizer for Confluence Content
Sanitizes raw XHTML/HTML returned by Confluence Cloud storage format,
stripping executable tags (script, object, iframe), malicious attributes (onclick, onload),
and converting clean HTML to structured markdown/text.
"""

import re
from bs4 import BeautifulSoup

def sanitize_confluence_html(raw_html: str) -> str:
    """
    Sanitizes HTML content from Confluence storage format.
    Removes potentially dangerous tags and extracts readable text/markdown structure.
    """
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove dangerous elements
    for tag in soup(["script", "style", "iframe", "object", "embed", "applet", "meta", "link"]):
        tag.decompose()

    # Remove dangerous attributes like onclick, onload, javascript: links
    for el in soup.find_all(True):
        attrs = dict(el.attrs)
        for attr in attrs:
            if attr.startswith("on") or "javascript:" in str(attrs[attr]).lower():
                del el.attrs[attr]

    # Convert headings to markdown
    for level in range(6, 0, -1):
        for h in soup.find_all(f"h{level}"):
            h.replace_with(f"\n\n{'#' * level} {h.get_text().strip()}\n\n")

    # Convert list items
    for li in soup.find_all("li"):
        li.replace_with(f"\n- {li.get_text().strip()}")

    # Convert tables to readable text if any
    for tr in soup.find_all("tr"):
        cells = [td.get_text().strip() for td in tr.find_all(["td", "th"])]
        if cells:
            tr.replace_with("\n| " + " | ".join(cells) + " |")

    text = soup.get_text()
    # Normalize multiple newlines and spaces
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return text.strip()
