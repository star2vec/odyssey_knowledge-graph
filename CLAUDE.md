# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A knowledge graph (KG) pipeline that builds a property graph from Homer's *Odyssey* using local LLMs and FalkorDB. The core research question: schema-guided extraction (`SchemaLLMPathExtractor`) vs. open-domain extraction (`DynamicLLMPathExtractor`) over the same literary source text.

## Infrastructure Setup

```bash
# Start FalkorDB (required before any extraction)
docker-compose up -d
```

FalkorDB runs on `localhost:6379` (Redis protocol) with a web UI on port 3000. All config (model, chunking, DB connection, source URL) lives in `config.yaml`.

## Running the Pipeline

All scripts run from the project root with `--book N` (book number from Homer's Odyssey):

```bash
pip install -r requirements.txt

python src/extract_schema.py --book 1  # schema-guided → FalkorDB graph: odyssey_schema
python src/extract_open.py --book 1    # open-domain   → FalkorDB graph: odyssey_open
python src/query.py                    # run predefined Cypher queries on both graphs
python src/analyze.py                  # compare quantitative metrics between graphs
```

`scrape.py` is a shared library (not run directly); it fetches and chunks the source text from theoi.com.

## Architecture

5-stage ETL pipeline, each stage an independent Python script:

```
scrape.py (shared lib) → extract_schema.py → odyssey_schema (FalkorDB)
                       → extract_open.py   → odyssey_open  (FalkorDB)
                                              ↓
                                           query.py / analyze.py
```

**`schema.py`** — Ontology definitions only. Enums for `EntityType` (CHARACTER, DEITY, CREATURE, LOCATION, ARTIFACT, EVENT) and `RelationType` (PARENT_OF, KILLS, TRAVELS_TO, DISGUISES_AS, etc.). Edit here to change the schema-guided extraction's vocabulary.

**`extract_schema.py`** — Uses `SchemaLLMPathExtractor(strict=True)` with the enums from `schema.py`. Strict mode means only defined entity/relation types are extracted.

**`extract_open.py`** — Uses `DynamicLLMPathExtractor(num_workers=4)` with no predefined schema.

**`query.py`** — 4 hardcoded Cypher queries run against both graphs side-by-side: ego network, journey path (schema only), divine interventions, disguise/recognition events.

**LLM/Embeddings**: Ollama running locally, model `llama3.2` (set in `config.yaml`). Both LLM inference and embeddings use Ollama.

## No Tests or Linting

There are no test files, linting configs, or CI setup. This is a research/learning project.
