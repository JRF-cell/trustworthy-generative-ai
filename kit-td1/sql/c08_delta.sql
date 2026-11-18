-- Both faulty queries retain only birth_date = '2001-09-24'.
-- The correct age window is ]2000-09-24, 2001-09-24].
-- No extra customer is added; list every customer wrongly omitted.
SELECT c.customer_id, c.birth_date,
       SUM(o.quantity_product * p.price) AS missed_revenue_cents
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE c.birth_date > '2000-09-24'
  AND c.birth_date <= '2001-09-24'
  AND c.birth_date <> '2001-09-24'
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
