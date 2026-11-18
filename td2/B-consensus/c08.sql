-- TD2 Pair B: wrong consensus on question C08.
-- C08: revenue excluding VAT, in euro cents, of the customers who are
-- exactly 25 years old on 2026-09-24 (all their orders).
-- "Exactly 25 years old" = completed age of 25 = born from 2000-09-25 to 2001-09-24.
--
-- Run from the repository root:
--   sqlite3 td1/data/boutique.sqlite < td2/B-consensus/c08.sql


-- 1. Reference query (td1/reference-td1.csv). Expected result: 605580.
-- Completed age = year difference, minus 1 if the birthday is not yet reached on 2026-09-24.
SELECT 'reference' AS query, COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders AS o
JOIN product AS p ON p.product_id = o.product_id
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE (CAST(strftime('%Y', '2026-09-24') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER)
       - (strftime('%m-%d', '2026-09-24') < strftime('%m-%d', c.birth_date))) = 25;


-- 2. Query returned by openai/gpt-oss-20b (td1/traces-td1.csv). Expected result: 25920 (wrong).
-- Error: it only keeps customers born ON 2001-09-24 (25th birthday that day),
-- instead of the whole year from 2000-09-25 to 2001-09-24.
SELECT 'gpt-oss-20b' AS query, COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date >= '2001-09-24'
  AND c.birth_date <  '2001-09-25';


-- 3. Query returned by dots-studio/dots-3-note-preview:free (td1/traces-td1.csv). Expected result: 25920 (wrong).
-- Same error written differently: birth year + 25 = 2026 AND same month and day as 2026-09-24,
-- so again only the customers born on 2001-09-24.
SELECT 'dots-3-note-preview' AS query, COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
    AND substr(c.birth_date, 6, 2) = substr('2026-09-24', 6, 2)
    AND substr(c.birth_date, 9, 2) = substr('2026-09-24', 9, 2)
);


-- 4. Delta query: customers counted by the reference (condition of query 1)
-- but missed by the faulty queries (NOT the condition of query 2).
-- Expected result: 5 customers (C004, C005, C007, C009, C008), total 579660 = 605580 - 25920.
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE (CAST(strftime('%Y', '2026-09-24') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER)
       - (strftime('%m-%d', '2026-09-24') < strftime('%m-%d', c.birth_date))) = 25
  AND NOT (c.birth_date >= '2001-09-24' AND c.birth_date < '2001-09-25')
GROUP BY c.customer_id, c.birth_date
ORDER BY c.birth_date;
