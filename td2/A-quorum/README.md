# Pair A - The k-of-n vote

**Members:** FERHAT Jawed, PONS-BOUREGBA Roman, HENNOUCHE Yanice

## Work

- `vote_k_sur_n` completed in [td1/skeleton-multi-llm-en.py](../../td1/skeleton-multi-llm-en.py). The method stays in the kit because `td1/atelier-vote.py` loads it from the same folder.
- [vote_td2.py](vote_td2.py): runs the vote on the 20 questions with the fixed 2-of-3 panel (`gpt-oss-120b`, `north-mini-code:free`, `qwen3.8-27b`, k = 2) and with a 3-of-5 quorum on the five TD1 models (k = 3).
- [vote-comparison-td2.csv](vote-comparison-td2.csv): the output table (values of the five models, both decisions, agreement with the reference).

## Commands

```bash
cd td1
python3 atelier-vote.py                                    # four synthetic examples
python3 atelier-vote.py --traces traces-td1.csv --case C02 # fixed panel on one question
cd ..
python3 td2/A-quorum/vote_td2.py                           # 2-of-3 versus 3-of-5
```

## Results

- 2-of-3: 17 consensus (all correct), 3 abstentions (C10, C17, C19).
- 3-of-5: 17 consensus (all correct), 3 abstentions (C02, C08, C10).
- The decision changes on C02, C08, C17 and C19. The explanation of each case is in [reports/td2.md](../../reports/td2.md), section 3.
