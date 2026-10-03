import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import gradio as gr

from book_search_service import format_year, search_local_title, search_rapidapi

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

books = pd.read_csv(BASE_DIR / "books_with_emotions.csv")
books["large_thumbnail"] = books["thumbnail"].fillna(str(BASE_DIR / "cover-not-found.jpg"))
books.loc[
    books["large_thumbnail"].str.startswith("http", na=False), "large_thumbnail"
] += "&fife=w800"

PERSIST_DIRECTORY = BASE_DIR / "chroma_db"
_db_books = None


def get_database() -> Chroma:
    global _db_books

    if _db_books is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Add it to a .env file or your environment."
            )
        _db_books = Chroma(
            persist_directory=str(PERSIST_DIRECTORY),
            embedding_function=OpenAIEmbeddings(),
        )
    return _db_books


def retrieve_semantic_recommendations(
        query: str,
        category: str | None = None,
        tone: str | None = None,
        initial_top_k: int = 50,
        final_top_k: int = 16,
) -> pd.DataFrame:
    recs = get_database().similarity_search(query, k=initial_top_k)
    books_list = []

    for rec in recs:
        isbn_str = rec.page_content.split()[0].strip('"')
        if isbn_str.isdigit():
            books_list.append(int(isbn_str))

    book_recs = books[books["isbn13"].isin(books_list)]

    if category and category != "All":
        book_recs = book_recs[book_recs["simple_categories"] == category]

    if tone == "Happy":
        book_recs = book_recs.sort_values(by="joy", ascending=False)
    elif tone == "Surprising":
        book_recs = book_recs.sort_values(by="surprise", ascending=False)
    elif tone == "Angry":
        book_recs = book_recs.sort_values(by="anger", ascending=False)
    elif tone == "Suspenseful":
        book_recs = book_recs.sort_values(by="fear", ascending=False)
    elif tone == "Sad":
        book_recs = book_recs.sort_values(by="sadness", ascending=False)

    return book_recs.head(final_top_k)


def _book_details(book: dict) -> str:
    link = f"[Read more]({book['url']})" if book.get("url") else "No external link available."
    return (
        f"### {book['title']}\n\n"
        f"**Author:** {book['authors']}  \n"
        f"**Published:** {book['year']}  \n"
        f"**Rating:** {book['rating']}  \n"
        f"**Source:** {book['source']}  \n\n"
        f"{book['description']}\n\n{link}"
    )


def _semantic_books(query: str, category: str, tone: str) -> list[dict]:
    recommendations = retrieve_semantic_recommendations(query, category, tone)
    results = []
    for _, row in recommendations.iterrows():
        description = row["description"]
        description = "No description available." if pd.isna(description) else str(description)
        authors = row["authors"] if pd.notna(row["authors"]) else "Unknown author"
        results.append(
            {
                "title": row["title"],
                "authors": authors.replace(";", ", "),
                "year": format_year(row["published_year"]),
                "rating": row["average_rating"],
                "cover": row["large_thumbnail"],
                "url": row.get("url", ""),
                "description": description,
                "source": "Semantic dataset",
            }
        )
    return results


def _gallery_items(books_found: list[dict]) -> list[tuple[str, str]]:
    return [
        (
            book["cover"] or str(BASE_DIR / "cover-not-found.jpg"),
            f"{book['title']} by {book['authors']} ({book['year']}) | Rating: {book['rating']}",
        )
        for book in books_found
    ]


def search_books(query: str, mode: str, category: str, tone: str):
    if not query.strip():
        return [], gr.Dropdown(choices=[], value=None), "Enter a search query.", [], ""

    if mode == "Exact title search":
        found = search_local_title(books, query)
        status = "Found in the local dataset."
        if not found:
            try:
                found = search_rapidapi(query)
                status = "Found through HAPI Books on RapidAPI."
            except Exception as error:
                return [], gr.Dropdown(choices=[], value=None), "", [], f"RapidAPI search failed: {error}"
            if not found:
                status = (
                    "No title found locally or on HAPI Books."
                    if os.getenv("RAPIDAPI_KEY")
                    else "No title found. Add RAPIDAPI_KEY for external title lookup."
                )
    else:
        found = _semantic_books(query, category, tone)
        status = "Semantic search using Chroma, category, and tone filters."

    titles = [book["title"] for book in found]
    selected = titles[0] if titles else None
    details = _book_details(found[0]) if found else "No books found."
    return _gallery_items(found), gr.Dropdown(choices=titles, value=selected), details, found, status


def show_book_details(title: str, found: list[dict]):
    selected = next((book for book in found if book["title"] == title), None)
    return _book_details(selected) if selected else "Select a book to view details."


def update_search_mode(mode: str):
    semantic_mode = mode == "Semantic recommendations"
    if semantic_mode:
        query = gr.Textbox(
            label="Describe the kind of book you want",
            placeholder="e.g., A story about forgiveness",
        )
    else:
        query = gr.Textbox(
            label="Search for an exact title",
            placeholder="e.g., The Alchemist",
        )
    return gr.Column(visible=semantic_mode), query


categories = ["All"] + sorted(books["simple_categories"].dropna().unique())
tones = ["All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad"]

css = """
:root {
    --page-black: #080b12;
    --panel-black: #101827;
    --panel-border: #263b5d;
    --blue-text: #b9d8ff;
    --blue-bright: #4ea1ff;
}
.gradio-container {
    background: var(--page-black) !important;
    color: var(--blue-text) !important;
}
#page-title h1 {
    color: var(--blue-bright) !important;
}
#search-panel, #details-panel {
    background: var(--panel-black) !important;
    border: 1px solid var(--panel-border) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
#search-mode label, #search-mode span, label span {
    color: var(--blue-text) !important;
}
button.primary {
    background: var(--blue-bright) !important;
    color: #06101f !important;
}
"""

with gr.Blocks(theme=gr.themes.Base(primary_hue="blue", neutral_hue="slate"), css=css) as dashboard:
    gr.Markdown("# Page Plunge", elem_id="page-title")

    with gr.Column(elem_id="search-panel"):
        search_mode = gr.Radio(
            choices=["Semantic recommendations", "Exact title search"],
            value="Semantic recommendations",
            label="Choose a search mode",
            elem_id="search-mode",
        )
        user_query = gr.Textbox(
            label="Describe the kind of book you want",
            placeholder="e.g., A story about forgiveness",
        )
        with gr.Column() as semantic_filters:
            with gr.Row():
                category_dropdown = gr.Dropdown(choices=categories, label="Category", value="All")
                tone_dropdown = gr.Dropdown(choices=tones, label="Emotional tone", value="All")
        submit_button = gr.Button("Find recommendations", variant="primary")

    search_status = gr.Markdown()
    gr.Markdown("## Recommendations", elem_id="recommendations-title")
    output = gr.Gallery(label="Recommended books", columns=8, rows=2, object_fit="contain", height="auto")
    with gr.Column(elem_id="details-panel"):
        book_selector = gr.Dropdown(label="Choose a book for details", choices=[])
        book_details = gr.Markdown("Select a book to view details.")
    results_state = gr.State([])

    search_mode.change(
        fn=update_search_mode,
        inputs=search_mode,
        outputs=[semantic_filters, user_query],
    )

    submit_button.click(
        fn=search_books,
        inputs=[user_query, search_mode, category_dropdown, tone_dropdown],
        outputs=[output, book_selector, book_details, results_state, search_status],
    )
    book_selector.change(
        fn=show_book_details,
        inputs=[book_selector, results_state],
        outputs=book_details,
    )

if __name__ == "__main__":
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
    )