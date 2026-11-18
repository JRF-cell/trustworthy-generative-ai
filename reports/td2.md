# TD2 Report - The Quorum, then the Routing Rule

**Course:** Trustworthy Generative AI - ESILV  
**Date:** November 18, 2026  
**Class:** DIA 5  
**Subgroup:** 2  
**Members:** FERHAT Jawed, PONS-BOUREGBA Roman, MAITREHENRY Hugo, SIMON Alvina, HENNOUCHE Yanice, HAMOURI Badis, IMGHI Fatima

## 1. Objective

TD2 builds two decisions of a service on top of the TD1 results:

1. a k-of-n vote between several models, which keeps a value or abstains;
2. a routing rule that sends each question family to the cheapest model that was correct on it in TD1.

We also look for a wrong consensus in our TD1 traces and prove its cause in SQL.

## 2. Environment

- Statement: TD2, pack `2026-11-18-students-5` (final version online). The kit scripts used (`atelier-vote.py`, `atelier-routage.py`, `skeleton-multi-llm-en.py`) have the same content as the online kit.
- Python: 3.15.0 (`kit-td1/.venv`)
- Database: `data/boutique.sqlite`, opened read-only
- Data: the 103 real TD1 traces in [traces-td1.csv](../kit-td1/traces-td1.csv), the references in [reference-td1.csv](../kit-td1/reference-td1.csv) and the table [model-question-comparison-en.csv](../kit-td1/model-question-comparison-en.csv)

No new network call was made in TD2. Everything below is computed from the stored TD1 traces.

TD2 files:

- [kit-td1/skeleton-multi-llm-en.py](../kit-td1/skeleton-multi-llm-en.py): `vote_k_sur_n` completed (it stays in the kit because `atelier-vote.py` loads it from there);
- [td2/vote_td2.py](../td2/vote_td2.py) and its output [td2/vote-comparison-td2.csv](../td2/vote-comparison-td2.csv): step 1;
- [td2/atelier-routage.py](../td2/atelier-routage.py): our adapted simulator (the original stays in `kit-td1/`);
- [td2/routage-before-td2.txt](../td2/routage-before-td2.txt) and [td2/routage-after-td2.txt](../td2/routage-after-td2.txt): simulator outputs.

## 3. Step 1 - The k-of-n vote

### Implementation

`Orchestrateur.vote_k_sur_n` is completed in [skeleton-multi-llm-en.py](../kit-td1/skeleton-multi-llm-en.py):

1. `k` must be a strict majority (`n // 2 < k <= n`), otherwise `ValueError`;
2. two proposals with the same `(provider, model_requested)` raise `ValueError`;
3. only proposals with `verdict = executed` and a value vote; an error stays in n without a vote;
4. if a value reaches k votes, it returns the consensus with the agreeing models;
5. otherwise it returns an abstention with the largest number of votes and `value = None`.

We tested the refusals: `k = 1` and `k = 4` with n = 3 are refused, and a duplicate pair is refused.

### Synthetic examples (`python3 atelier-vote.py`)

These values are synthetic, not results on the shop data.

| Example | Proposals | Decision | Reference | Match |
|---|---|---|---:|---|
| agreement | 100, 100, 120 | consensus 100 (2 votes) | 100 | yes |
| disagreement | 100, 110, 120 | abstention (max 1 vote) | 100 | - |
| unavailable | 100, error, error | abstention (max 1 vote) | 100 | - |
| wrong consensus | 0, 0, 100 | consensus 0 (2 votes) | 100 | no |

### 2-of-3 versus 3-of-5 on the twenty questions

- 2-of-3: fixed panel of `atelier-vote.py` (`gpt-oss-120b`, `north-mini-code:free`, `qwen3.8-27b`), k = 2.
- 3-of-5: the five TD1 models, k = 3, same `vote_k_sur_n` method.
- For each model we take its last attempt on the question, as in `atelier-vote.py`. The reference is compared after the vote.

Command (from the repository root): `python3 td2/vote_td2.py`, output in [td2/vote-comparison-td2.csv](../td2/vote-comparison-td2.csv).

| Case | Reference | 2-of-3 decision | Match | 3-of-5 decision | Match | Changes |
|---|---:|---|---|---|---|---|
| C01 | 792800 | consensus 792800 (2 votes) | yes | consensus 792800 (4 votes) | yes | no |
| C02 | 590320 | consensus 590320 (2 votes) | yes | abstention (max 2) | - | **yes** |
| C03 | 936350 | consensus 936350 (3 votes) | yes | consensus 936350 (5 votes) | yes | no |
| C04 | 2826250 | consensus 2826250 (3 votes) | yes | consensus 2826250 (5 votes) | yes | no |
| C05 | 38480 | consensus 38480 (3 votes) | yes | consensus 38480 (5 votes) | yes | no |
| C06 | 0 | consensus 0 (3 votes) | yes | consensus 0 (5 votes) | yes | no |
| C07 | 13970 | consensus 13970 (3 votes) | yes | consensus 13970 (5 votes) | yes | no |
| C08 | 605580 | consensus 605580 (2 votes) | yes | abstention (max 2) | - | **yes** |
| C09 | 487980 | consensus 487980 (2 votes) | yes | consensus 487980 (3 votes) | yes | no |
| C10 | 558980 | abstention (max 1) | - | abstention (max 2) | - | no |
| C11 | 446690 | consensus 446690 (2 votes) | yes | consensus 446690 (3 votes) | yes | no |
| C12 | 1666490 | consensus 1666490 (3 votes) | yes | consensus 1666490 (5 votes) | yes | no |
| C13 | 107740 | consensus 107740 (3 votes) | yes | consensus 107740 (5 votes) | yes | no |
| C14 | 0 | consensus 0 (3 votes) | yes | consensus 0 (5 votes) | yes | no |
| C15 | 168680 | consensus 168680 (2 votes) | yes | consensus 168680 (3 votes) | yes | no |
| C16 | 376740 | consensus 376740 (2 votes) | yes | consensus 376740 (3 votes) | yes | no |
| C17 | 258180 | abstention (max 1) | - | consensus 258180 (3 votes) | yes | **yes** |
| C18 | 62480 | consensus 62480 (3 votes) | yes | consensus 62480 (4 votes) | yes | no |
| C19 | 1990 | abstention (max 1) | - | consensus 1990 (3 votes) | yes | **yes** |
| C20 | 1106090 | consensus 1106090 (3 votes) | yes | consensus 1106090 (5 votes) | yes | no |

**Summary:**

- 2-of-3: 17 consensus (all correct), 3 abstentions (C10, C17, C19).
- 3-of-5: 17 consensus (all correct), 3 abstentions (C02, C08, C10).
- No quorum returned a wrong value on our batch.

**Explanation of the four differences:**

- **C02**: `gpt-oss-120b` and `qwen3.8-27b` return 590320, so the fixed panel keeps it even though `north-mini-code` has an invalid SQL (`sql_invalid`, syntax error near "AS"). In the 3-of-5 quorum, `gpt-oss-20b` and Dots both return the same wrong value 0, so 590320 and 0 each get 2 votes. Nothing reaches 3, so the quorum abstains.
- **C08**: same pattern. 120b and Qwen give 605580, `north-mini-code` gives 0, and `gpt-oss-20b` and Dots both give 25920. The 3-of-5 quorum abstains with 2 votes. This is our wrong consensus case (step 2).
- **C17**: the fixed panel gives three different values: 258180 (120b), 371990 (Cohere) and 248490 (Qwen, obtained after one HTTP 429 retry). So it abstains. In 3-of-5, `gpt-oss-20b` and Dots also return 258180, which gives 3 votes and a correct consensus.
- **C19**: Qwen has two HTTP 429 errors (`not_executed`), so it stays in n without a vote, and Cohere returns 0. The fixed panel has only one vote for 1990 and abstains. In 3-of-5, `gpt-oss-20b` and Dots also return 1990, which gives a correct consensus with 3 votes.

C10 abstains in both cases: Cohere has an invalid SQL, Qwen returns 119410, Dots returns 0, and only 120b and 20b return 558980 (2 votes, below k = 3).

So the 3-of-5 quorum is not always better. It fixes C17 and C19, where the fixed panel lost a vote because of an error or a disagreement. But it loses C02 and C08, because two members share the same wrong value.

## 4. Step 2 - The wrong consensus (case C08)

### Identification and quorum verdict

Source and nature: **real batch**, our own TD1 traces (`nature = real`, 2026-10-21).

| Item | Value |
|---|---|
| Question | C08: total revenue excluding VAT, in euro cents, of customers who are exactly 25 years old on 2026-09-24 (all their orders) |
| Agreeing models | `groq:openai/gpt-oss-20b` (13:39:30 UTC) and `openrouter:dots-studio/dots-3-note-preview:free` (13:41:48 UTC) |
| Shared wrong value | 25920 cents (`verdict = incorrect` for both) |
| Independent reference | 605580 cents ([reference-td1.csv](../kit-td1/reference-td1.csv)) |
| Fixed 2-of-3 panel (k = 2) | votes: 605580 (120b), 0 (Cohere), 605580 (Qwen) -> **consensus 605580, correct**. The wrong value gets 0 votes because 20B and Dots are not in the panel |
| 3-of-5 quorum (k = 3) | votes: 605580 x2, 25920 x2, 0 x1 -> **abstention (max 2 votes)**. The wrong value is not kept, but it blocks the correct one |

These votes can be counted by hand from the values above, and `vote_k_sur_n` gives the same result (`td2/vote_td2.py`).

With a declared 2-of-3 panel made of `gpt-oss-20b`, Dots and Cohere, the wrong value 25920 would win with 2 votes. Agreement between two models is not a proof of correctness.

Other shared wrong values in our batch: C02 (20B and Dots = 0), C09 (Cohere and Dots = 0) and C11 (Cohere and Dots = 0).

### Faulty SQL clause

Reference query (C08 in `reference-td1.csv`), returns 605580:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders AS o
JOIN product AS p ON p.product_id = o.product_id
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE (CAST(strftime('%Y', '2026-09-24') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER)
       - (strftime('%m-%d', '2026-09-24') < strftime('%m-%d', c.birth_date))) = 25;
```

Query of `gpt-oss-20b`, returns 25920:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date >= '2001-09-24'
  AND c.birth_date <  '2001-09-25';
```

Query of Dots, returns 25920:

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
    AND substr(c.birth_date, 6, 2) = substr('2026-09-24', 6, 2)
    AND substr(c.birth_date, 9, 2) = substr('2026-09-24', 9, 2)
);
```

The `JOIN` conditions are the same in the three queries. The error is in the `WHERE` clause:

- "exactly 25 years old on 2026-09-24" means a completed age of 25, so a birth date from **2000-09-25 to 2001-09-24** (a window of one year);
- both faulty queries only keep customers born **on 2001-09-24**, i.e. people whose 25th birthday is that day (a window of one day);
- the two models wrote different SQL (a date range for 20B, `substr` comparisons for Dots) but made the same wrong reading of the question. This is why they agree on the same wrong value.

### Delta diagnostic query on `data/boutique.sqlite`

Rows counted by the reference but missed by the faulty queries (reference condition AND NOT faulty condition):

```sql
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE (CAST(strftime('%Y', '2026-09-24') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER)
       - (strftime('%m-%d', '2026-09-24') < strftime('%m-%d', c.birth_date))) = 25
  AND NOT (c.birth_date >= '2001-09-24' AND c.birth_date < '2001-09-25')
GROUP BY c.customer_id, c.birth_date
ORDER BY c.birth_date;
```

Result:

| customer_id | birth_date | revenue_cents |
|---|---|---:|
| C004 | 2000-09-25 | 150260 |
| C005 | 2000-09-26 | 150240 |
| C007 | 2000-11-30 | 118740 |
| C009 | 2001-03-10 | 61330 |
| C008 | 2001-05-15 | 99090 |
| **Total** | | **579660** |

579660 = 605580 - 25920, so these five customers explain the whole gap. The faulty queries only count C002 (born 2001-09-24, 25920 cents). No row is wrongly added: C002 is also in the reference set.

### Consequence and independent check

- A quorum cannot detect this error when the members who agree share the same reading of the question. Adding models that make the same mistake can even block the right answer (3-of-5 abstains).
- Independent check: run the deterministic reference query (completed age computed with the month-day comparison) and compare it with the model value. Another useful check is to look at the birth-date window the SQL actually tests: one day instead of one year is a clear sign of error.
- A different panel or an escalation is only a candidate check, not a guarantee.

### Mechanism illustrated: DEMO-VOTE (synthetic)

This is constructed teaching material, not model output. It uses a one-row table `sales('2026-01-01', 100)` and the period from 2026-01-01 inclusive to 2026-01-02 exclusive:

- `sale_date > '2026-01-01' AND sale_date < '2026-01-02'` returns **0**: the strict `>` excludes the first day;
- `sale_date >= '2026-01-01' AND sale_date < '2026-01-02'` returns **100**, which is the reference.

With proposals [0, 0, 100] and k = 2, the vote keeps 0: a wrong consensus caused by the same boundary error.

## 5. Step 3 - The routing rule

### TD1 rates per family

From [model-question-comparison-en.csv](../kit-td1/model-question-comparison-en.csv):

| Family | TD1 cells | gpt-oss-120b | gpt-oss-20b | north-mini-code | qwen3.8-27b | dots-3-note |
|---|---|---|---|---|---|---|
| F1 period | C01, C04, C05, C06, C07, C20 | 6/6 | 6/6 | 6/6 | 5/6 (C01 sql_rejected) | 6/6 |
| F2 age at a date | C02, C08, C09, C11 | 4/4 | 2/4 (C02, C08) | 0/4 | 4/4 | 0/4 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 (sql_invalid) | 0/1 (119410) | 0/1 (0) |
| F3 product list | C03, C12, C13, C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Combinations | C15, C16, C17, C18, C19 | 5/5 | 5/5 | 3/5 | 1/5 | 2/5 |

### Prices (portfolio)

- **Free routes:** in TD1, all five models were called on free routes (Groq Free API, OpenRouter `:free`).
- **Paid equivalent:** to rank them, we use the billed equivalent of the same model, from [methode-cout-en.md](../kit-td1/methode-cout-en.md) and the portfolio:
  - `gpt-oss-20b`: 0.075 / 0.30 USD per M tokens;
  - `gpt-oss-120b`: 0.15 / 0.60;
  - `qwen3.8-27b`: 0.80 / 4.00;
  - Cohere and Dots: N/A (no paid route documented).
- **Cost per request:** in TD1, `gpt-oss-120b` used on average 641 input and 264 output tokens. On the portfolio route `gpt-oss-120b#openrouter` (pay-per-token, 0.15 / 0.60), this gives (641 x 0.15 + 264 x 0.60) / 1,000,000 = **0.00025 USD per request**.

### The rule (one page)

| Family | First model (cheapest correct in TD1) | Dashboard | Customer figure | Amount paid out | If the first model is unavailable |
|---|---|---|---|---|---|
| F1 period | `gpt-oss-20b` Groq free (6/6) | none | 2-of-3 quorum (fixed panel 6/6 correct) | reference SQL + human review | `gpt-oss-120b` Groq free (6/6), then `north-mini-code` OpenRouter free (6/6, other provider), then wait for the refill if the request can wait, else abstain |
| F2 age at a date | `gpt-oss-120b` Groq free (4/4) | none | 2-of-3 quorum (fixed panel 4/4 correct; 3-of-5 abstained on C02, C08) | reference SQL + human review | `qwen3.8-27b` Groq free (4/4), then wait for the Groq refill if possible, then `gpt-oss-120b` paid route (0.00025 USD) if the budget allows, else abstain |
| F2b age at the order | `gpt-oss-20b` Groq free (1/1) | none | reference SQL (both quorums abstained on C10) | reference SQL + human review | `gpt-oss-120b` Groq free (1/1), then wait, then paid `gpt-oss-120b`, else abstain |
| F3 product list | `gpt-oss-20b` Groq free (4/4) | none | 2-of-3 quorum (fixed panel 4/4 correct) | reference SQL + human review | `gpt-oss-120b` Groq free, then `north-mini-code` OpenRouter free (4/4), then wait, else abstain |
| Combinations | `gpt-oss-20b` Groq free (5/5) | none | 3-of-5 quorum (5/5 correct; 2-of-3 abstained on C17, C19) | reference SQL + human review | `gpt-oss-120b` Groq free (5/5), then wait, then paid `gpt-oss-120b`, else abstain |

Reasons:

- **First model**: all routes used are free, so we rank by the billed equivalent of the same model. `gpt-oss-20b` is the cheapest documented route, and we use it on every family where it was 100 % correct. On F2 it made 2 errors (C02, C08), so the first model is `gpt-oss-120b` (cheaper than Qwen).
- **Dashboard = none**: this is only admissible because the first model was 100 % correct on the family in TD1 and the cost of an error is low. For F2b this rests on one cell only (C10), which is very little evidence.
- **Customer figure**: we choose the quorum that gave only correct consensus on the family in TD1. F2b has no working quorum on C10, so we use the deterministic reference query.
- **Amount paid out**: an error costs money, so we always require the reference SQL and a human review.
- **No free model is enough on its own outside Groq for F2, F2b and combinations**: on OpenRouter, Cohere and Dots got 0/4 on F2 and 0/1 on F2b. These families set the price of checking for TD3.

Twenty questions only support a hypothesis for this batch, not a general error rate or a permanent ranking.

### Simulator: before adaptation

`python3 kit-td1/atelier-routage.py` (original kit file), full output in [td2/routage-before-td2.txt](../td2/routage-before-td2.txt):

| Scenario | Action | Resource | Reason |
|---|---|---|---|
| simple | run | small-free | eligible included capacity |
| complex | run | senior-subscription | eligible included capacity |
| deferrable | defer (60 min) | senior-subscription | recheck availability at wake-up |
| urgent | run (0.30 USD) | senior-api | available route within the authorised budget |
| budget exhausted | abstain | - | no eligible resource within deadline and budget |
| high impact | run | senior-subscription | eligible included capacity (checks: source verification and human review) |
| unknown capability | abstain | - | no eligible resource within deadline and budget |

### Simulator: after adaptation

What we changed in our copy [td2/atelier-routage.py](../td2/atelier-routage.py):

- **`RESOURCES`**: the five TD1 models on their free routes, plus the paid portfolio route `gpt-oss-120b#openrouter` (0.00025 USD per request). The `level` becomes `families`: a model is eligible on a family only if it was 100 % correct on it in TD1. The resources are listed cheapest first.
- **`choose`**: it uses `family` and `use` (dashboard, customer, payout) instead of `difficulty` and `high_impact`. The checks come from our rule, and every `reason` cites the TD1 cells.
- **Scenarios**: the seven scenarios are kept. The "exhausted" state now means the Groq free quota is used up (HTTP 429, as for Qwen on C17 to C19 in TD1). The reset time of 60 minutes is fictitious.

`python3 td2/atelier-routage.py`, full output in [td2/routage-after-td2.txt](../td2/routage-after-td2.txt):

| Scenario | Request | Action | Resource | Checks | Reason |
|---|---|---|---|---|---|
| simple | F1, dashboard | run | gpt-oss-20b#groq-free | none | eligible included capacity, TD1 F1 cells C01,C04,C05,C06,C07,C20: 6/6 correct |
| complex | F2, dashboard | run | gpt-oss-120b#groq-free | none | eligible included capacity, TD1 F2 cells C02,C08,C09,C11: 4/4 correct |
| deferrable | F2, Groq exhausted | defer (60 min) | gpt-oss-120b#groq-free | none | recheck availability at wake-up, TD1 F2 cells ...: 4/4 correct |
| urgent | F2, cannot wait, 5 min | run (0.00025 USD) | gpt-oss-120b#openrouter-paid | none | available route within the authorised budget, TD1 F2 cells ...: 4/4 correct |
| budget exhausted | F2, budget 0 | abstain | - | none | no eligible resource within deadline and budget for TD1 F2 cells C02,C08,C09,C11 |
| high impact | F2, payout | run | gpt-oss-120b#groq-free | reference SQL + human review | eligible included capacity, TD1 F2 cells ...: 4/4 correct |
| unknown capability | F4 | abstain | - | - | family F4 not measured in TD1, no eligible model |

In the "deferrable" case, the OpenRouter free models are not eligible on F2 (0/4 in TD1). So the request waits for Groq instead of being sent to a model that failed this family.

### Priority order in the supplied `choose`

`choose` tests its branches in this order:

1. **`included`**: an eligible resource that is available now with `cash == 0`;
2. **`waiting`**: an eligible resource with `cash == 0` that is unavailable but refills before the deadline, used only if the request can wait;
3. **`paid`**: an available resource whose cash fits the budget;
4. otherwise, **abstain**.

So an available subscription (`cash == 0`, `allocation > 0`) is always picked in branch 1, before the code even looks at deferring to an exhausted free resource. The `min(..., allocation)` only sorts among resources that are available now. The reason is that the subscription is already paid (no new cash) and gives the answer immediately, while deferring adds delay and the free quota is not even certain at wake-up (it must be measured again).

This priority should be reversed when the subscription quota is scarce and needed for other work. If a request that can wait uses the subscription quota now, a later urgent or difficult request may find it exhausted and have to use the paid API (new cash) or abstain. So when the free route refills before the deadline and the subscription quota is the bottleneck, a request that can wait should defer to the free route and keep the subscription for urgent requests.

## 6. Prompts

No model was called in TD2 and the prompts did not change since TD1. The prompt hash of each call is kept in `prompt_sha256` in `traces-td1.csv`.

## 7. Limitations

- **Small sample**: only 20 questions and one attempt per model (plus the 429 retries of Qwen). The rates per family are a hypothesis for this batch, not general error rates.
- **F2b**: it has only one cell (C10), so its rule is based on very little evidence.
- **Simulator values**: the availability and reset times are fictitious. The paid cost uses the mean TD1 tokens of `gpt-oss-120b` and the portfolio price, not a real bill.
- **Cohere and Dots**: they have no documented paid route, so their billed equivalent stays N/A.
- **Wrong consensus**: no quorum returned a wrong value on our batch, but the case C08 shows that this depends on who is in the panel.

## 8. Team Contributions

| Pair | Step | Members |
|---|---|---|
| Pair A | Step 1: `vote_k_sur_n`, 2-of-3 versus 3-of-5 table | FERHAT Jawed, PONS-BOUREGBA Roman, HENNOUCHE Yanice |
| Pair B | Step 2: wrong consensus C08, delta query | MAITREHENRY Hugo, SIMON Alvina |
| Pair C | Step 3: routing rule, simulator | HAMOURI Badis, IMGHI Fatima |

## 9. Next Steps

- TD3: compute the cost of the checks chosen here (quorums, reference SQL, review) for the families where no free model is enough on its own (F2, F2b, combinations).
- Repeat the measures on more questions per family, especially F2b.
- Measure the real availability of the free routes instead of the fictitious reset times.

## 10. AI Assistance

AI assistance was used to help write the vote method, the comparison script and this report. All values come from the TD1 traces and from queries executed on `data/boutique.sqlite`. The group is responsible for checking the results.
