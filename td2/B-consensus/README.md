# B — Consensus erroné

Alvina Simon, Hugo Maitrehenry.

- [diagnostic_sql.py](diagnostic_sql.py) : recherche des erreurs partagées et diagnostic C08.
- [verification_csv.py](verification_csv.py) : second calcul des références sur les CSV.
- [Requête delta](sql/c08_delta.sql) et [clients omis](resultats/c08-delta.csv).
- [Explication complète](../../reports/td2-diagnostic-c08.md).

Depuis ce dossier : `python diagnostic_sql.py`.

Dots et 20B donnent 25 920 au lieu de 605 580 centimes. Ils confondent avoir
25 ans et fêter ses 25 ans ce jour-là. Les cinq clients omis expliquent
les 579 660 centimes de différence.

Relectures : [1](review-1.md), [2](review-2.md).
