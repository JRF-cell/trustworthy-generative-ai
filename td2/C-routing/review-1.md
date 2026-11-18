# Review of Pair C (routing) by Pair A

Reviewers: FERHAT Jawed, PONS-BOUREGBA Roman, HENNOUCHE Yanice

## What we checked

- `python3 td1/atelier-routage.py` and `python3 td2/C-routing/atelier-routage.py` give exactly the same outputs as `routage-before-td2.txt` and `routage-after-td2.txt`.
- The TD1 rates per family in the rule are the same as in `td1/model-question-comparison-en.csv` (for example F2: `gpt-oss-120b` 4/4, `gpt-oss-20b` 2/4, `north-mini-code` 0/4).
- Eligibility: in the "deferrable" scenario the OpenRouter models are not used for F2, because they got 0/4 on this family in TD1.

## Remarks

- 6 of the 7 decisions cite TD1 cells in their reason. The 7th is "unknown capability" (family F4), which has no TD1 cells: the reason says it, which is correct.

## Conclusion

OK, nothing to correct.
