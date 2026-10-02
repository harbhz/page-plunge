import os
from typing import Any

import requests

RAPIDAPI_HOST = "hapi-books.p.rapidapi.com"
RAPIDAPI_SEARCH_URL = f"https://{RAPIDAPI_HOST}/search/{{title}}"


def _cover_url(url: Any) -> str:
    if not isinstance(url, str) or not url:
        return ""
    return url.replace("._SX50_", "").replace("._SY75_", "")


def _normalise_book(book: dict[str, Any]) -> dict[str, Any]:
    authors = book.get("authors") or []
    if isinstance(authors, str):
        authors = [authors]

    return {
        "title": book.get("name") or book.get("title") or "Untitled",
        "authors": ", ".join(str(author) for author in authors) or "Unknown author",
        "year": book.get("year") or book.get("published_year") or "Unknown year",
        "rating": book.get("rating") or book.get("average_rating") or "Not rated",
        "cover": _cover_url(book.get("cover") or book.get("thumbnail")),
        "url": book.get("url") or "",
        "description": book.get("description") or "No description available.",
        "source": book.get("source") or "Local dataset",
    }


def search_rapidapi(title: str) -> list[dict[str, Any]]:
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return []

    response = requests.get(
        RAPIDAPI_SEARCH_URL.format(title=requests.utils.quote(title)),
        headers={
            "X-RapidAPI-Host": RAPIDAPI_HOST,
            "X-RapidAPI-Key": api_key,
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    return [_normalise_book(book) for book in payload if isinstance(book, dict)]


def search_local_title(books, title: str) -> list[dict[str, Any]]:
    query = title.strip().casefold()
    if not query:
        return []

    exact = books[books["title"].fillna("").str.casefold() == query]
    matches = exact if not exact.empty else books[
        books["title"].fillna("").str.casefold().str.contains(query, regex=False)
    ].head(16)

    return [
        _normalise_book(
            {
                "title": row["title"],
                "authors": row["authors"],
                "year": row["published_year"],
                "rating": row["average_rating"],
                "thumbnail": row["thumbnail"],
                "description": row["description"],
                "url": row.get("url", ""),
            }
        )
        for _, row in matches.iterrows()
    ]
