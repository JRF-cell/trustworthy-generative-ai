# Pair C - The routing rule

**Members:** HAMOURI Badis, IMGHI Fatima

## Work

- The routing rule per family (F1, F2, F2b, F3, combinations), with the TD1 rates and cells: [reports/td2.md](../../reports/td2.md), section 5.
- [atelier-routage.py](atelier-routage.py): our adapted copy of the simulator. `RESOURCES` holds the five TD1 models and the paid portfolio route `gpt-oss-120b#openrouter`. `choose` uses the family and the use (dashboard, customer, payout), and every reason cites the TD1 cells. The original is kept unchanged in `td1/atelier-routage.py`.
- [routage-before-td2.txt](routage-before-td2.txt): output of the original simulator.
- [routage-after-td2.txt](routage-after-td2.txt): output of our adapted simulator.

## Commands

From the repository root:

```bash
python3 td1/atelier-routage.py                   # before
python3 td2/C-routing/atelier-routage.py         # after
```

## Rule (summary)

| Family | First model | Dashboard | Customer figure | Amount paid out |
|---|---|---|---|---|
| F1 period | `gpt-oss-20b` (6/6) | none | 2-of-3 quorum | reference SQL + human review |
| F2 age at a date | `gpt-oss-120b` (4/4) | none | 2-of-3 quorum | reference SQL + human review |
| F2b age at the order | `gpt-oss-20b` (1/1) | none | reference SQL | reference SQL + human review |
| F3 product list | `gpt-oss-20b` (4/4) | none | 2-of-3 quorum | reference SQL + human review |
| Combinations | `gpt-oss-20b` (5/5) | none | 3-of-5 quorum | reference SQL + human review |

## Reviewed and checked by Fatima IMGHI
