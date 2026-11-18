# C — Routage

Badis Hamouri, Fatima Imghi.

- [atelier-routage.py](atelier-routage.py) : simulateur adapté aux résultats TD1.
- [atelier-routage-original.py](atelier-routage-original.py) : version fournie.
- [Résultats avant](resultats/routage-avant.jsonl) et [après](resultats/routage-apres.jsonl).
- [Règle de routage](../../reports/td2-regle-routage.md).

Depuis ce dossier :

```bash
python atelier-routage.py
python atelier-routage.py --scenario deferrable
```

À expliquer : `run`, `defer`, `abstain`, les contrôles avant affichage ou paiement,
et la priorité d'une ressource incluse disponible sur l'attente d'une route gratuite.

Relectures : [1](review-1.md), [2](review-2.md).
