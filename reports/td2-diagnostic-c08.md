# Diagnostic C08 — valeur erronée partagée dans les traces réelles

Dots et GPT-OSS 20B renvoient **25 920 centimes**, contre **605 580** pour la référence. Les deux requêtes ont été réexécutées sur la base du groupe. Écart : **579 660 centimes (5 796,60 €)**.

## Votes comptés à la main et vérifiés par le code

- Panel fixe 2/3 : 120B = 605580, Cohere = 0, Qwen = 605580. Consensus correct, deux voix.
- Panel 3/5 : les trois mêmes, plus Dots = 25920 et 20B = 25920. Deux voix pour 605580, deux pour 25920, une pour 0 : abstention, maximum deux voix.
- La valeur erronée partagée ne gagne aucun des deux quorums. Dots et 20B sont tous deux hors du panel fixe ; leur ajout supprime ici un consensus correct.

## Cause SQL

Les personnes de 25 ans révolus le 24 septembre 2026 sont nées dans **]2000-09-24, 2001-09-24]**. Les deux modèles ne sélectionnent que la naissance du **24 septembre 2001** : ils confondent « avoir 25 ans » et « fêter son 25e anniversaire ce jour-là ». Dots exige séparément l’année 2001, le mois 09 et le jour 24. 20B emploie la fenêtre d’un seul jour [2001-09-24, 2001-09-25[. Pour les dates ISO présentes, les deux prédicats sont équivalents.

Les JOIN et le calcul quantité × prix sont corrects ; la cause est le WHERE sur la naissance. Aucune borne sur la date des commandes n’est demandée : toutes leurs commandes comptent.

## Dots — SQL complet

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

## 20B — SQL complet

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date >= '2001-09-24'
  AND c.birth_date <  '2001-09-25';
```

## Référence du groupe

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders AS o JOIN product AS p ON p.product_id = o.product_id JOIN customers AS c ON c.customer_id = o.customer_id WHERE (CAST(strftime('%Y', '2026-09-24') AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) - (strftime('%m-%d', '2026-09-24') < strftime('%m-%d', c.birth_date))) = 25;
```

## Diagnostic des lignes omises

```sql
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
```

| Client omis | Naissance | CA HT omis, centimes |
|---|---|---:|
| C004 | 2000-09-25 | 150260 |
| C005 | 2000-09-26 | 150240 |
| C007 | 2000-11-30 | 118740 |
| C008 | 2001-05-15 | 99090 |
| C009 | 2001-03-10 | 61330 |

**Total omis : 579 660.** Le client né le 24/09/2001 reste inclus pour 25 920 ; 25 920 + 579 660 = 605 580. Les requêtes fautives ajoutent zéro client hors référence.

Vérification indépendante : jointure des CSV en Python, calcul de l’âge par différence des années puis retrait de 1 si l’anniversaire n’est pas encore passé. Le total vaut aussi 605 580. Voir `evidence/reference-check.csv` et [verification_csv.py](../td2/B-consensus/verification_csv.py).

Conséquence : augmenter n ne garantit ni plus de couverture ni plus de justesse. Pour un résultat client ou un paiement, vérifier déterministement les conditions d’âge. Le consensus n’est jamais une preuve SQL.
