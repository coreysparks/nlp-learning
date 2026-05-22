# NLP Learning Project

## Purpose

This is a personal learning project focused on building hands-on experience with NLP (Natural Language Processing) techniques and generative AI techniques for understanding customer complaint data.

## Goals

- Learn basic Python workflows for analyzing text data
- Practice traditional NLP techniques (tokenization, TF-IDF, sentiment analysis, topic modeling)
- Explore generative AI / LLM-based techniques (embeddings, classification, summarization via Claude API)
- Use real-feeling customer complaint data as the consistent practice dataset throughout

## Dataset

A local SQLite database (`data/complaints.db`) contains synthetic customer complaint records used for all exercises. The schema is documented in `data/seed.py`.

## Project Structure

```
nlp-learning/
├── CLAUDE.md
├── pyproject.toml
├── data/
│   ├── seed.py          # creates and populates complaints.db
│   └── complaints.db    # SQLite database (generated)
└── notebooks/           # Jupyter notebooks for experiments
```

## Tech Stack

- Python 3.13+
- SQLite (via built-in `sqlite3`)
- Standard NLP libs: `nltk`, `scikit-learn`, `spacy` as needed
- Generative AI: Anthropic SDK (`anthropic`)
- Notebooks: `jupyter`

## Conventions

- Keep experiments in dated or clearly named notebooks under `notebooks/`
- Prefer simple, readable scripts over abstracted frameworks — this is a learning project
- Add comments when a technique needs explanation; otherwise keep code clean
