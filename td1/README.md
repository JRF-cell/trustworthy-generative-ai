# TD1 - Evaluating Language Models

This folder is the official student kit (`kit-td1`, pack `2026-10-18-students-1`) with our TD1 files added inside it. The description of every kit file is in the official kit page `README.html`.

For TD1, we compare five language models on the same 20 SQL questions and compare their values with our SQL references.

## Our TD1 files

| File | Content |
|---|---|
| `reference-td1.csv` | The 20 SQL reference queries and their values |
| `traces-A-new.csv` + `state-A-new.jsonl` | Model A: `openai/gpt-oss-120b` (Groq) |
| `traces-B.csv` | Model B: `openai/gpt-oss-20b` (Groq) |
| `traces-C.csv` + `state-C.jsonl` | Model C: `cohere/north-mini-code:free` (OpenRouter) |
| `traces-D.csv` + `state-D.jsonl` | Model D: `qwen/qwen3.8-27b` (Groq) |
| `traces-E.csv` + `state-E.jsonl` | Model E: `dots-studio/dots-3-note-preview:free` (OpenRouter) |
| `merge_traces.py` -> `traces-td1.csv` | The traces of the five models merged in one file |
| `build_td1_comparisons.py` -> `model-question-comparison-en.csv`, `five-model-summary-en.csv` | The TD1 tables (one result per model and question, results per family) |

## Commands

From this folder:

```bash
python3 verify-data.py              # database integrity, should return "ok": true
python3 merge_traces.py             # rebuilds traces-td1.csv
python3 build_td1_comparisons.py    # rebuilds the two TD1 tables
```

## Report

[reports/td1.md](../reports/td1.md)
