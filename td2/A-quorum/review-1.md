# Review of Pair A (quorum) by Pair B

Reviewers: MAITREHENRY Hugo, SIMON Alvina

## What we checked

- `python3 atelier-vote.py` (from `td1/`): the four synthetic examples give the expected decisions:
  agreement -> consensus 100 (2 votes), disagreement -> abstention, unavailable -> abstention, wrong consensus -> consensus 0 (2 votes).
- The refusals of `vote_k_sur_n`: `k = 1` and `k = 4` with n = 3 raise `ValueError`, and a duplicate (provider, model) pair raises `ValueError`.
- An error stays in n without a vote: with proposals [5, error, error] and k = 2, the method abstains (1 vote) and does not invent a value.
- `python3 td2/A-quorum/vote_td2.py` gives exactly the same `vote-comparison-td2.csv` as the one in the repository.

## Remarks

- Because k is a strict majority, only one value can reach k, so returning the first value that reaches k is not ambiguous.
- The vote never receives the reference: the comparison is done after the decision, as asked in the statement.

## Conclusion

OK, nothing to correct.
