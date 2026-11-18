# A — Quorum

Yanice Hennouche, Roman Pons-Bouregba, Jawed Ferhat.

- [vote.py](vote.py) : vote à majorité stricte.
- [atelier-vote.py](atelier-vote.py) : quatre exemples synthétiques.
- [comparaison.py](comparaison.py) : comparaison 2/3 et 3/5 sur les vingt questions.
- [Résultats](resultats/comparison.csv).

Depuis ce dossier :

```bash
python atelier-vote.py
python comparaison.py
```

À expliquer : un modèle indisponible reste dans n, un doublon est refusé,
et le passage à 3/5 change les réponses de C02, C08, C17 et C19.
La méthode `vote_k_sur_n` du [squelette fourni](../../kit-td1/skeleton-multi-llm-en.py)
appelle la fonction de `vote.py`.

Relectures : [1](review-1.md), [2](review-2.md).
