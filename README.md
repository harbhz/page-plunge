---
title: Page Plunge
emoji: 📚
colorFrom: indigo
colorTo: pink
sdk: gradio
sdk_version: 5.45.0
app_file: app.py
pinned: false
short_description: Semantic book recommendations with NLP and vector search
---

# Page Plunge

Page Plunge combines semantic recommendations with exact-title book search. Describe the kind of book you want, or switch to exact title mode to find a specific book and inspect its details.

**Live demo:** [huggingface.co/spaces/harbhz/page-plunge](https://huggingface.co/spaces/harbhz/page-plunge)

## How It Works

1. Semantic mode uses OpenAI embeddings and Chroma to retrieve relevant descriptions.
2. Category and emotional-tone controls refine semantic recommendations.
3. Exact title mode checks the local dataset first and can optionally query HAPI Books through RapidAPI.
4. Results include covers, authors, publication years, ratings, descriptions, and external links when available.

The exploratory notebooks document the data cleaning, categorization, sentiment analysis, and vector-search work behind the app.

## Requirements

- Python 3.10 or newer
- An OpenAI API key for semantic search
- The checked-in book data files
- A generated `chroma_db/` directory, unless one is already supplied by the deployment

## Local Setup

```bash
git clone https://github.com/harbhz/page-plunge.git
cd page-plunge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your key to `.env`:

```dotenv
OPENAI_API_KEY=your-openai-api-key
```

For optional external exact-title lookup, add a RapidAPI key:

```dotenv
RAPIDAPI_KEY=your-rapidapi-key
```

The RapidAPI key is server-side only and is used with the HAPI Books API. Exact-title searches still work against the local dataset without it.

### Get A HAPI Books API Key

1. Create or sign in to an account at [RapidAPI](https://rapidapi.com/).
2. Search the RapidAPI marketplace for **HAPI Books** and open the `hapi-books.p.rapidapi.com` API.
3. Subscribe to a plan. The free plan, when available, has request limits set by RapidAPI.
4. Open the API's **Endpoints** or **Code Snippets** page and copy the generated RapidAPI key.
5. Store it locally as `RAPIDAPI_KEY` in `.env`, or add it as a secret in the Hugging Face Space settings.

Page Plunge calls the HAPI search endpoint only when exact-title mode has no local match. Do not use a `NEXT_PUBLIC_` variable or expose this key in browser code.

If `chroma_db/` is not present, build it from the included data:

```bash
python build_database.py
```

Start the app:

```bash
python app.py
```

Gradio will print the local URL in the terminal.

## Deployment

The app is live on Hugging Face Spaces: [huggingface.co/spaces/harbhz/page-plunge](https://huggingface.co/spaces/harbhz/page-plunge)

The Space uses the Gradio SDK configured in this README's front matter and installs `requirements.txt`. Add `OPENAI_API_KEY` and `RAPIDAPI_KEY` as secrets under the Space's **Settings → Variables and secrets**. Pushing to the Space's git remote triggers a rebuild.

The committed `chroma_db/` directory is read at runtime; it is not rebuilt during deployment. A free Space sleeps after a period of inactivity and takes a moment to start on the next visit.

## Data And Generated Files

The CSV files and cover image are part of the sample dataset used by the application. `chroma_db/` is a generated vector index stored with Git LFS. After regenerating it with `build_database.py`, delete any collection folders the new database no longer references, then commit the whole directory so the deployment stays consistent. Do not commit `.env`, API keys, virtual environments, IDE settings, or other generated files.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `app.py` | Gradio application and recommendation logic |
| `book_search_service.py` | Exact-title search over the local dataset and HAPI Books |
| `build_database.py` | Builds the Chroma vector database |
| `*.csv` | Cleaned book and model output data |
| `data-exploration.ipynb`, `sentiment-analysis.ipynb`, `text-classification.ipynb` | Data exploration and model experiments |
| `vector_search.ipynb` | Vector-search prototype |

## Validation

Run the lightweight syntax check before opening a pull request:

```bash
python -m compileall -q app.py build_database.py book_search_service.py
```

## License

No license has been selected for this repository yet. Until one is added, the code should not be assumed to be available for reuse.
