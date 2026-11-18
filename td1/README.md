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

## Errors and response times

From `traces-td1.csv` (column `latency_ms` = response time of one call):

| Model | Attempts | Errors | Median time | Slowest call |
|---|---:|---|---:|---|
| `gpt-oss-120b` (Groq) | 20 | none | 856 ms | 1950 ms (C08) |
| `gpt-oss-20b` (Groq) | 20 | none | 884 ms | 1387 ms (C11) |
| `north-mini-code:free` (OpenRouter) | 20 | 2 invalid SQL (C02, C10: syntax error) | 2093 ms | 8746 ms (C11) |
| `qwen3.8-27b` (Groq) | 23 | 1 rejected SQL (C01: answer inside a ```sql block, not a plain SELECT), 4 HTTP 429 rate limit (C17, C18, C19 twice) | 534 ms | 767 ms (C15) |
| `dots-3-note-preview:free` (OpenRouter) | 20 | none | 2767 ms | 4704 ms (C16) |

- **Errors:** Qwen had the most problems. The Groq free rate limit (HTTP 429) stopped it 4 times: C17 and C18 worked on the retry, but C19 failed twice and has no value. The median time of Qwen does not count the four 429 answers (67 to 134 ms).
- **Response times:** the two OpenRouter free models are the slowest (median 2 to 3 s, up to 8.7 s for Cohere on C11). The three Groq models answer in less than 2 s.

## Commands

From this folder:

```bash
python3 verify-data.py              # database integrity, should return "ok": true
python3 merge_traces.py             # rebuilds traces-td1.csv
python3 build_td1_comparisons.py    # rebuilds the two TD1 tables
```

## Report

[reports/td1.md](../reports/td1.md)
