# Trustworthy Generative AI

ESILV | A4 Data & AI | 2026–2027

This repository contains our work for the Next-Generation AI course at ESILV.

The goal is to evaluate how reliably different language models generate SQL queries. We compare their answers with reference results calculated directly from a SQLite database.


## Team

**Class:** DIA 5  
**Subgroup:** 2

### Members

- FERHAT Jawed
- PONS-BOUREGBA Roman
- MAITREHENRY Hugo
- SIMON Alvina
- HENNOUCHE Yanice
- HAMOURI Badis
- IMGHI Fatima


## TD1: Evaluating Language Models

For TD1, we compare five language models on 20 questions about sales revenue.

Our work consists of:
1. Writing SQL queries to calculate the correct answers.
2. Independently verifying these reference results.
3. Running the same questions through five AI models.
4. Comparing the results and analyzing errors, response times and costs.

The five models are accessed through Groq and OpenRouter.

Folder: [td1/](td1/) (the official student kit with our TD1 files, see `td1/README.md`).  
Report: [reports/td1.md](reports/td1.md).

## TD2: The Quorum, then the Routing Rule

For TD2, we reuse the TD1 traces (no new model call). The subgroup is split into three pairs, one folder per pair:

| Pair | Folder | Step | Members |
|---|---|---|---|
| A | [td2/A-quorum/](td2/A-quorum/) | Step 1: k-of-n vote, 2-of-3 versus 3-of-5 on the 20 questions | FERHAT Jawed, PONS-BOUREGBA Roman, HENNOUCHE Yanice |
| B | [td2/B-consensus/](td2/B-consensus/) | Step 2: wrong consensus C08, faulty SQL clause, delta query | MAITREHENRY Hugo, SIMON Alvina |
| C | [td2/C-routing/](td2/C-routing/) | Step 3: routing rule per family, adapted simulator | HAMOURI Badis, IMGHI Fatima |

Each pair folder has a `README.md` and two reviews (`review-1.md`, `review-2.md`) written by the two other pairs. The vote `vote_k_sur_n` is completed in `td1/skeleton-multi-llm-en.py`, because `td1/atelier-vote.py` loads it from the same folder.

Folder: [td2/](td2/) (see `td2/README.md`).  
Report: [reports/td2.md](reports/td2.md).

## TD3

The same repository will be used for TD3. Its work and report will be added after the session.

## Project Structure

```
README.md
td1/            official student kit + our TD1 files (README.md)
td2/            README.md
  A-quorum/     Pair A: README.md, review-1.md, review-2.md, vote script and table
  B-consensus/  Pair B: README.md, review-1.md, review-2.md
  C-routing/    Pair C: README.md, review-1.md, review-2.md, adapted simulator and outputs
reports/        td1.md, td2.md
```

## Setup

Requirements:
- Python 3.10 or newer
- The `requests` Python package
- Free Groq and OpenRouter accounts

From the repository root:

```bash
cd td1
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install requests
python3 verify-data.py
```

The verification should return `"ok": true`.

To check access to the five AI models, first configure the `GROQ_API_KEY` and `OPENROUTER_API_KEY` environment variables following the official environment guide.

Then run:

```bash
python3 check_access.py | tee ready-for-td1.txt
```

This command makes five API requests. API keys must never be committed to GitHub.

The commands for running the TD1 experiments and reproducing the results will be documented as the group completes the work.

## Technical Information

- Course pack: `2026-10-18-students-1`
- Python version used: 3.14.6
- Database: SQLite (`boutique.sqlite`)
- Providers: Groq and OpenRouter

Database SHA-256:

`0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`

## Current Progress

- [x] Downloaded the official October 18 student kit.
- [x] Verified database integrity.
- [x] Calculated and saved SQL answers for C07, C08 and C09.
- [ ] Independently verify these answers with teammates.
- [ ] Complete the remaining SQL references.
- [ ] Run the model experiments.
- [ ] Analyze results and complete `reports/td1.md`.

## AI Assistance

AI tools were used to help prepare the repository and write SQL queries. The group is responsible for checking the results and documenting the prompts used.

## References

- [Course website](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/index.html)
- [TD1 instructions](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td1-en.html)
- [Submission requirements](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/submission-en.html)
