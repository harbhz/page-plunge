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
5. Store it locally as `RAPIDAPI_KEY` in `.env`, or add it as a secret environment variable on Render.

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

## Render Deployment

The repository includes a `render.yaml` blueprint for a free Render web service. Create a new Blueprint Instance from this repository, then add `OPENAI_API_KEY` as a secret environment variable in Render. Render uses `python app.py` as the start command and supplies the service port automatically.

The committed `chroma_db/` directory is read at runtime; it is not rebuilt during deployment. The service may sleep on the free plan and take a moment to respond to its first request after waking.

## Data And Generated Files

The CSV files and cover image are part of the sample dataset used by the application. `chroma_db/` is a generated vector index and is ignored for new commits; regenerate it with `build_database.py` when needed. Do not commit `.env`, API keys, virtual environments, IDE settings, or other generated files.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `app.py` | Gradio application and recommendation logic |
| `build_database.py` | Builds the Chroma vector database |
| `*.csv` | Cleaned book and model output data |
| `*_analysis.ipynb` | Data exploration and model experiments |
| `vector_search.ipynb` | Vector-search prototype |

## Validation

Run the lightweight syntax check before opening a pull request:

```bash
python -m compileall -q app.py build_database.py
```

## License

No license has been selected for this repository yet. Until one is added, the code should not be assumed to be available for reuse.
