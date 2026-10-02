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

Page Plunge is a semantic book recommender. Describe the kind of book you want, optionally choose a category and emotional tone, and the app searches an OpenAI-embedded Chroma vector database for recommendations.

## How It Works

1. Book descriptions are embedded with OpenAI embeddings.
2. Chroma retrieves the closest descriptions for a user's query.
3. Results are filtered by category and sorted by the selected emotional tone.
4. The Gradio interface displays book covers and short descriptions.

The exploratory notebooks document the data cleaning, categorization, sentiment analysis, and vector-search work behind the app.

## Requirements

- Python 3.10 or newer
- An OpenAI API key
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

If `chroma_db/` is not present, build it from the included data:

```bash
python build_database.py
```

Start the app:

```bash
python app.py
```

Gradio will print the local URL in the terminal.

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
