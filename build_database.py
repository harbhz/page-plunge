import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_chroma import Chroma

load_dotenv()

PERSIST_DIRECTORY = "chroma_db"


def build_and_save_db():
    print("Loading book data from books_with_emotions.csv...")
    try:
        books_df = pd.read_csv("books_with_emotions.csv")
    except FileNotFoundError:
        print("Error: books_with_emotions.csv not found. Please ensure the file is in the directory.")
        return

    documents = []
    for _, row in books_df.iterrows():
        tagged_desc = row.get("tagged_description")
        if pd.notna(tagged_desc) and 'nan nan' not in str(tagged_desc):
            documents.append(Document(page_content=str(tagged_desc)))

    if not documents:
        print("No valid documents found to add to the database.")
        return

    print(f"Found {len(documents)} valid documents.")
    print("Creating embeddings and building Chroma database. This may take a few minutes...")

    db = Chroma.from_documents(
        documents,
        OpenAIEmbeddings(),
        persist_directory=PERSIST_DIRECTORY
    )

    print(f"Database successfully created and saved to '{PERSIST_DIRECTORY}'.")


if __name__ == "__main__":
    build_and_save_db()