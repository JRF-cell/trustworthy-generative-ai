# TD2 - The Quorum, then the Routing Rule

For TD2, we reuse the TD1 traces (`td1/traces-td1.csv`, `td1/reference-td1.csv`). No new model call was made.

## Who did what

| Pair | Folder | Step | Members |
|---|---|---|---|
| A | [A-quorum/](A-quorum/) | Step 1: k-of-n vote, 2-of-3 versus 3-of-5 on the 20 questions | FERHAT Jawed, PONS-BOUREGBA Roman, HENNOUCHE Yanice |
| B | [B-consensus/](B-consensus/) | Step 2: wrong consensus C08, faulty SQL clause, delta query | MAITREHENRY Hugo, SIMON Alvina |
| C | [C-routing/](C-routing/) | Step 3: routing rule per family, adapted simulator | HAMOURI Badis, IMGHI Fatima |

Each folder has a `README.md` (work and results) and two review files written by the two other pairs.

## Commands

From the repository root:

```bash
python3 td2/A-quorum/vote_td2.py                 # Pair A: 2-of-3 versus 3-of-5
python3 td1/atelier-routage.py                   # Pair C: original simulator (before)
python3 td2/C-routing/atelier-routage.py         # Pair C: adapted simulator (after)
```

## Report

[reports/td2.md](../reports/td2.md)
