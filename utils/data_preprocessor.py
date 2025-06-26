"""Basic HTML to text cleaning utilities."""
from __future__ import annotations

from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    return " ".join(text.split())
