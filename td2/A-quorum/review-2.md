# Review of Pair A (quorum) by Pair C

Reviewers: HAMOURI Badis, IMGHI Fatima

## What we checked

- The references used by `vote_td2.py` come from `td1/reference-td1.csv`. They are the same as the `reference` column of the 103 rows of `td1/traces-td1.csv` (no difference).
- The "last attempt" rule on the two cases with HTTP 429:
  - C17: Qwen has a 429 then a value 248490, so Qwen votes 248490;
  - C19: Qwen has two 429, so Qwen stays in n without a vote.
- The four decisions that change between 2-of-3 and 3-of-5 (C02, C08, C17, C19) match the values in `vote-comparison-td2.csv`.

## Remarks

- 3-of-5 is not always better than 2-of-3: it fixes C17 and C19 but abstains on C02 and C08, because `gpt-oss-20b` and Dots share the same wrong value. We used this result in the routing rule (2-of-3 for F2, 3-of-5 for combinations).

## Conclusion

OK, nothing to correct.
