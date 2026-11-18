# TD2 — Vote et routage

DIA 5, groupe 2 — 18 novembre 2026.
[Répartition des équipes](../td2/README.md).

## Données

Nous utilisons les [traces TD1](../kit-td1/traces-td1.csv) et les
[références du groupe](../kit-td1/reference-td1.csv), sans nouvel appel aux modèles.
Les 103 lignes donnent 100 cellules finales : la dernière tentative du CSV est
retenue pour chaque modèle et question, comme dans l'atelier fourni.
Les trois tentatives supplémentaires sont celles de Qwen sur C17, C18 et C19.

Les 20 références ont été vérifiées par SQL et par un calcul Python indépendant
sur les CSV. La base passe les contrôles d'intégrité.
[Preuves](../kit-td1/evidence/reference-check.csv),
[provenance et empreintes](../kit-td1/evidence/provenance.json).
Sous Windows, `.gitattributes` garde les fins de ligne LF des données et du schéma
pour que leurs empreintes correspondent au manifeste.

## A — Vote

Le vote exige une majorité stricte et refuse les doublons fournisseur/modèle.
Un modèle indisponible reste dans n mais ne vote pas. La référence est comparée
après le vote, jamais utilisée pour choisir la réponse.

Le panel 2/3 contient 120B, Cohere et Qwen. Le panel 3/5 ajoute Dots et 20B.
120B et 20B appartiennent à la même famille : leurs erreurs ne sont pas forcément indépendantes.

Les quatre exemples synthétiques passent : accord → 100 ; désaccord → abstention ;
un seul modèle disponible → abstention ; [0, 0, 100] → consensus erroné à 0.
Sur la table jouet, `>` exclut la vente du 01/01/2026 (0), `>=` l'inclut (100).
[Sorties](../kit-td1/evidence/vote-synthetique.jsonl).

| Cas | Référence | 2/3 : valeur, voix, résultat | 3/5 : valeur, voix, résultat |
|---|---:|---|---|
| C01 | 792800 | 792800, 2, correct | 792800, 4, correct |
| C02 | 590320 | 590320, 2, correct | —, 2, abstention |
| C03 | 936350 | 936350, 3, correct | 936350, 5, correct |
| C04 | 2826250 | 2826250, 3, correct | 2826250, 5, correct |
| C05 | 38480 | 38480, 3, correct | 38480, 5, correct |
| C06 | 0 | 0, 3, correct | 0, 5, correct |
| C07 | 13970 | 13970, 3, correct | 13970, 5, correct |
| C08 | 605580 | 605580, 2, correct | —, 2, abstention |
| C09 | 487980 | 487980, 2, correct | 487980, 3, correct |
| C10 | 558980 | —, 1, abstention | —, 2, abstention |
| C11 | 446690 | 446690, 2, correct | 446690, 3, correct |
| C12 | 1666490 | 1666490, 3, correct | 1666490, 5, correct |
| C13 | 107740 | 107740, 3, correct | 107740, 5, correct |
| C14 | 0 | 0, 3, correct | 0, 5, correct |
| C15 | 168680 | 168680, 2, correct | 168680, 3, correct |
| C16 | 376740 | 376740, 2, correct | 376740, 3, correct |
| C17 | 258180 | —, 1, abstention | 258180, 3, correct |
| C18 | 62480 | 62480, 3, correct | 62480, 4, correct |
| C19 | 1990 | —, 1, abstention | 1990, 3, correct |
| C20 | 1106090 | 1106090, 3, correct | 1106090, 5, correct |

Les valeurs sont en centimes ; en cas d'abstention, « voix » est le plus grand
nombre de votes pour une même valeur. Les deux quorums donnent chacun
**17 consensus corrects, 0 erroné et 3 abstentions** : couverture 17/20, exactitude
sur les réponses retenues 17/17.

Les différences s'expliquent ainsi :

- **C02** : 120B et Qwen donnent 590320 ; Cohere est `sql_invalid`. Dots et 20B ajoutent deux zéros incorrects : deux voix contre deux, donc perte du consensus en 3/5.
- **C08** : 120B et Qwen donnent 605580, Cohere 0, Dots et 20B 25920. Même partage 2/2/1 : le quorum 3/5 s'abstient.
- **C17** : le panel fixe donne 258180, 371990 et 248490. Dots et 20B ajoutent chacun 258180 : gain d'un consensus correct à trois voix.
- **C19** : 120B donne 1990, Cohere 0, Qwen est `not_executed`. Dots et 20B donnent 1990 : gain d'un consensus correct à trois voix.
- **C10** : 120B donne 558980, Cohere est `sql_invalid`, Qwen donne 119410. Dots ajoute 0 et 20B ajoute 558980 : le maximum passe de 1 à 2, insuffisant pour 3/5.
- **C01** : Qwen est `sql_rejected`. Les quatre autres donnent 792800 : de 2 à 4 voix correctes.
- **C09 et C11** : 20B ajoute la référence (487980 et 446690), Dots ajoute 0. Le consensus correct passe de 2 à 3 voix ; Cohere avait déjà donné 0.
- **C15 et C16** : 20B ajoute la référence (168680 et 376740), Dots donne 138920 et 1367540. Le consensus correct passe de 2 à 3 voix ; Qwen donnait respectivement 0 et 367050.
- **C18** : Dots donne 39580, 20B donne la référence 62480. Le consensus correct passe de 3 à 4 voix.
- **C03, C04, C05, C06, C07, C12, C13, C14, C20** : les cinq modèles donnent la référence du tableau, tous avec le verdict `correct`. Le consensus passe de 3 à 5 voix.

Les [détails CSV](../kit-td1/evidence/comparison.csv) conservent les valeurs et statuts de chaque modèle.

## B — Erreur partagée

Quatre cas contiennent une même valeur erronée donnée par deux modèles :
C02 (0), C08 (25920), C09 (0), C11 (0). Aucun ne produit de quorum erroné ici.
[Inventaire et requêtes](../kit-td1/evidence/shared-wrong-values.json).

Nous analysons **C08**, issu des traces réelles. Dots et 20B sélectionnent seulement
les clients nés le 24/09/2001. Pour avoir 25 ans le 24/09/2026, il faut être né dans
]24/09/2000, 24/09/2001]. Ils confondent l'âge révolu avec l'anniversaire exact.

La référence vaut **605580**, leurs réponses **25920**. Les cinq clients omis
représentent **579660 centimes**. Le 2/3 reste correct ; le 3/5 s'abstient.
Le [diagnostic complet](td2-diagnostic-c08.md) contient les deux requêtes, la
référence, le SELECT des clients omis et les résultats exécutés.

## C — Routage

La [règle de routage](td2-regle-routage.md) donne les taux exacts et les cellules
pour chaque famille. À prix égal, nous choisissons un modèle à 100 % sur la
famille, puis son identifiant alphabétique : 120B est retenu pour toutes les familles.
Un chiffre client exige une référence SQL ; un paiement exige aussi une revue humaine.

| Scénario | Avant | Après |
|---|---|---|
| simple | run : small-free | run : groq:openai/gpt-oss-120b |
| complex | run : senior-subscription | run : groq:openai/gpt-oss-120b |
| deferrable | defer : senior-subscription | defer : groq:openai/gpt-oss-120b |
| urgent | run : senior-api | abstain : None |
| budget exhausted | abstain : None | abstain : None |
| high impact | run : senior-subscription | run : groq:openai/gpt-oss-120b |
| unknown capability | abstain : None | abstain : None |

Avant : trois ressources fictives. Après : les cinq routes gratuites du TD1,
avec des disponibilités simulées. En cas de pénurie, toutes ces routes sont
épuisées ; aucune route payante mesurée ne permet de traiter l'urgence.
Chaque `reason` cite les questions et les ratios utilisés.
[Avant](../kit-td1/evidence/routage-avant.jsonl),
[après](../kit-td1/evidence/routage-apres.jsonl),
[cas par famille et usage](../kit-td1/evidence/routage-familles-usages.json).

Dans le code fourni, `included` est testé avant `waiting`. Un abonnement disponible
avec `cash == 0` est donc choisi avant d'attendre une route gratuite épuisée,
même si son allocation est payante. Le service immédiat est prioritaire.
On pourrait inverser cet ordre pour une demande non urgente si l'on veut réserver
l'allocation d'abonnement aux urgences. Il faudrait alors vérifier que le refill
respecte le délai, puis recontrôler la disponibilité au réveil.

## Vérification et limites

Depuis `kit-td1` :

```bash
python -m unittest test_td2.py
python analyse_td2.py
```

Les 17 tests passent. Le script recalcule les résultats, vérifie les références
et rapproche l'écart SQL. Les rapports sont maintenus séparément en Markdown.

Le vote, le diagnostic et le simulateur fonctionnent. C10 reste une abstention.
Les petits effectifs par famille, les erreurs corrélées et la disponibilité simulée
limitent ces conclusions : vingt questions ne garantissent pas les performances futures.
Les prompts TD1 n'ont pas changé. [Aide utilisée](td2-ai-assistance.md).

Les équipes et leurs deux fiches de revue sont dans [td2/](../td2/README.md).
La revue croisée reste à faire et à noter. Ensuite, déposer sur Moodle l'URL du
dépôt, le hash complet du commit final et le lien du rapport à ce commit avant
le **22 novembre 2026 à 23:59, heure de Paris**.
