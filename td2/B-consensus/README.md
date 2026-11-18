# Pair B - The wrong consensus (C08)

**Members:** MAITREHENRY Hugo, SIMON Alvina

## Case

- Source: real TD1 batch (`td1/traces-td1.csv`).
- Question C08: revenue of customers who are exactly 25 years old on 2026-09-24.
- `openai/gpt-oss-20b` and `dots-3-note-preview:free` both return **25920** cents. The reference is **605580** cents.
- Fixed 2-of-3 panel: consensus 605580 (correct). 3-of-5 quorum: abstention (605580 and 25920 both get 2 votes).

## Faulty SQL clause

Both models only keep customers born on 2001-09-24 (their 25th birthday is that day). "Exactly 25 years old" means a birth date from 2000-09-25 to 2001-09-24.

## Delta query on `td1/data/boutique.sqlite`

Rows counted by the reference but missed by the faulty queries:

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

| customer_id | birth_date | revenue_cents |
|---|---|---:|
| C004 | 2000-09-25 | 150260 |
| C005 | 2000-09-26 | 150240 |
| C007 | 2000-11-30 | 118740 |
| C009 | 2001-03-10 | 61330 |
| C008 | 2001-05-15 | 99090 |
| **Total** | | **579660** |

579660 = 605580 - 25920: these five customers explain the whole gap.

The full analysis (the three SQL queries, the quorum verdicts, the independent check and DEMO-VOTE) is in [reports/td2.md](../../reports/td2.md), section 4.
