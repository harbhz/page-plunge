import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import gradio as gr

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


def recommend_books(
        query: str,
        category: str,
        tone: str
):
    recommendations = retrieve_semantic_recommendations(query, category, tone)
    results = []

    for _, row in recommendations.iterrows():
        description = row["description"]
        if pd.isna(description):
            description = "No description available."

        truncated_desc_split = description.split()
        truncated_description = " ".join(truncated_desc_split[:30])
        if len(truncated_desc_split) > 30:
            truncated_description += "..."

        authors = row["authors"]
        if pd.notna(authors):
            authors_split = authors.split(";")
            if len(authors_split) == 2:
                authors_str = f"{authors_split[0]} and {authors_split[1]}"
            elif len(authors_split) > 2:
                authors_str = f"{', '.join(authors_split[:-1])}, and {authors_split[-1]}"
            else:
                authors_str = authors
        else:
            authors_str = "Unknown Author"

        caption = f"{row['title']} by {authors_str}: {truncated_description}"
        results.append((row["large_thumbnail"], caption))
    return results


categories = ["All"] + sorted(books["simple_categories"].dropna().unique())
tones = ["All", "Happy", "Surprising", "Angry", "Suspenseful", "Sad"]

with gr.Blocks(theme=gr.themes.Glass()) as dashboard:
    gr.Markdown("# Semantic book recommender")

    with gr.Row():
        user_query = gr.Textbox(label="Please enter a description of a book:",
                                placeholder="e.g., A story about forgiveness")
        category_dropdown = gr.Dropdown(choices=categories, label="Select a category:", value="All")
        tone_dropdown = gr.Dropdown(choices=tones, label="Select an emotional tone:", value="All")
        submit_button = gr.Button("Find recommendations")

    gr.Markdown("## Recommendations")
    output = gr.Gallery(label="Recommended books", columns=8, rows=2, object_fit="contain", height="auto")

    submit_button.click(fn=recommend_books,
                        inputs=[user_query, category_dropdown, tone_dropdown],
                        outputs=output)

if __name__ == "__main__":
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
    )