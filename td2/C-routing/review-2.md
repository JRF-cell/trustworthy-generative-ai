# Review of Pair C (routing) by Pair B

Reviewers: MAITREHENRY Hugo, SIMON Alvina

## What we checked

- The consistency constraint of the statement: "none" is only used for the internal dashboard, and only with a first model that was 100 % correct on the family in TD1. Customer figures use a quorum or the reference SQL, and amounts paid out always use the reference SQL and a human review.
- The cost of the paid route: with the TD1 mean tokens of `gpt-oss-120b` (641 input, 264 output, 20 calls) and the portfolio price 0.15 / 0.60 USD per M tokens, we find 0.000254 USD per request, rounded to 0.00025 in `RESOURCES`.
- F2 starts with `gpt-oss-120b`, not `gpt-oss-20b`: this is consistent with our case C08, where `gpt-oss-20b` was wrong.

## Remarks

- F2b relies on one cell only (C10), so its rule is weak.
- The availability and the reset of 60 minutes are fictitious: they are scenario values, not measured on Groq.

## Conclusion

OK, nothing to correct.
