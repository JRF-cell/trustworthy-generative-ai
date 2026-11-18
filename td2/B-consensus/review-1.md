# Review of Pair B (consensus) by Pair A

Reviewers: FERHAT Jawed, PONS-BOUREGBA Roman, HENNOUCHE Yanice

## What we checked

- We re-executed on `td1/data/boutique.sqlite` the five C08 queries stored in `td1/traces-td1.csv`. We get the same values as in the traces:
  `gpt-oss-120b` 605580, `gpt-oss-20b` 25920, `north-mini-code` 0, `qwen3.8-27b` 605580, Dots 25920.
- The quorum verdicts with our `vote_k_sur_n`: the fixed 2-of-3 panel keeps 605580 (2 votes) and the 3-of-5 quorum abstains (605580 and 25920 both have 2 votes). This matches Pair B's count.
- The delta query returns 5 customers for a total of 579660 cents, and 579660 = 605580 - 25920.

## Conclusion

OK, nothing to correct.
