# TD2 — Vote et routage

| Partie | Membres |
|---|---|
| [A — Quorum](A-quorum/README.md) | Yanice Hennouche, Roman Pons-Bouregba, Jawed Ferhat |
| [B — Consensus erroné](B-consensus/README.md) | Alvina Simon, Hugo Maitrehenry |
| [C — Routage](C-routing/README.md) | Badis Hamouri, Fatima Imghi |

[Rapport commun](../reports/td2.md).

Chaque dossier contient le code de l'équipe, ses résultats, son README et deux
fiches de revue. Les revues sont à compléter après les relectures.

```text
td2/
  analyse_td2.py          # lance les trois parties
  td2_common.py           # lecture des traces et fonctions communes
  test_td2.py
  A-quorum/
    vote.py
    atelier-vote.py
    comparaison.py
    resultats/
  B-consensus/
    diagnostic_sql.py
    verification_csv.py
    sql/
    resultats/
  C-routing/
    atelier-routage.py
    atelier-routage-original.py
    resultats/
```

Depuis `td2`, lancer `python analyse_td2.py`, puis `python -m unittest test_td2.py`.
Les données d'entrée restent dans `kit-td1/`. La méthode du squelette officiel
appelle `A-quorum/vote.py`, pour garder une seule implémentation du vote.
Les rapports sont à mettre à jour si les résultats changent.
