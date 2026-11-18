# TD2 — Le quorum, puis la règle de routage

**DIA 5 — sous-groupe 2 · 18 novembre 2026**

## Résultat

Sur les 20 questions, **2/3 et 3/5 produisent chacun 17 consensus corrects, 0 consensus erroné et 3 abstentions**. Leur couverture est de 85 %, et leur exactitude conditionnelle sur les consensus de 17/17. Ces proportions décrivent uniquement ce lot.

**3/5 perd les réponses correctes de C02 et C08, mais résout C17 et C19. C10 reste une abstention.** Les modèles peuvent partager une même erreur SQL : le cas réel C08 est démontré avec les clients omis et un écart exact de 579 660 centimes.

## Provenance et méthode

Dépôt source : [JRF-cell/trustworthy-generative-ai](https://github.com/JRF-cell/trustworthy-generative-ai), commit initial `3dc2201cf55a7ab6e83b5134431127df18c0bb63`. Entrées : [traces TD1](../kit-td1/traces-td1.csv), [références TD1](../kit-td1/reference-td1.csv). Le CSV contient 103 tentatives, ramenées aux 100 cellules finales par la dernière ligne pour chaque fournisseur/modèle/question, comme dans l’atelier fourni. Nature : `real`. Aucun nouvel appel de modèle.

La base et les trois CSV passent la vérification d’intégrité avant et après. Les 20 requêtes de référence du groupe ont été exécutées en lecture seule puis contrôlées par un calcul Python indépendant sur les CSV. Les références historiques et les traces sont conservées inchangées. [Preuves de provenance](../kit-td1/evidence/provenance.json), [double vérification](../kit-td1/evidence/reference-check.csv).

Les trois tentatives supplémentaires concernent Qwen : C17 passe de `not_executed` à `incorrect`, C18 de `not_executed` à `correct`, C19 reste `not_executed`. Les dates sont conservées telles qu’exportées ; la sélection suit l’ordre du CSV. Les documents TD1 narratifs du dépôt sont antérieurs aux résultats et n’ont pas été réécrits.

Sous Windows, Git avait converti les fins de ligne des CSV et du schéma en CRLF, modifiant leurs empreintes sans changer les données. Les fins de ligne officielles LF ont été rétablies ; `.gitattributes` les préserve pour les futurs clones. Les empreintes correspondent désormais toutes au manifeste officiel.

## 1. Vote k sur n

La méthode [vote_k_sur_n](../kit-td1/skeleton-multi-llm-en.py) valide n//2 < k ≤ n et l’unicité des couples fournisseur/modèle avant tout résultat. Seules les propositions exécutées avec une valeur entière votent. Une indisponibilité conserve sa place dans n. Aucun verdict de justesse ni référence n’est transmis au vote ; la comparaison intervient ensuite.

Panel fixe : 120B = `groq:openai/gpt-oss-120b`, Cohere = `openrouter:cohere/north-mini-code:free`, Qwen = `groq:qwen/qwen3.8-27b`. Le quorum 3/5 ajoute Dots = `openrouter:dots-studio/dots-3-note-preview:free` et 20B = `groq:openai/gpt-oss-20b`. Attention : 120B et 20B appartiennent à la même famille GPT-OSS ; cinq modèles ne signifient pas cinq erreurs indépendantes.

Quatre exemples synthétiques exécutés : accord [100,100,120] → 100 (2 voix) ; désaccord [100,110,120] → abstention (1) ; indisponibles [100,None,None] → abstention (1) ; mauvais consensus [0,0,100] → 0 (2), malgré la référence 100. La table jouet confirme `>` → 0 et `>=` → 100 sur la vente du 01/01/2026. [Sorties](../kit-td1/evidence/vote-synthetique.jsonl).

| Cas | Référence | 2/3 : valeur ; voix ; verdict | 3/5 : valeur ; voix ; verdict |
|---|---:|---|---|
| C01 | 792800 | 792800 ; 2 ; correct | 792800 ; 4 ; correct |
| C02 | 590320 | 590320 ; 2 ; correct | — ; 2 ; abstention |
| C03 | 936350 | 936350 ; 3 ; correct | 936350 ; 5 ; correct |
| C04 | 2826250 | 2826250 ; 3 ; correct | 2826250 ; 5 ; correct |
| C05 | 38480 | 38480 ; 3 ; correct | 38480 ; 5 ; correct |
| C06 | 0 | 0 ; 3 ; correct | 0 ; 5 ; correct |
| C07 | 13970 | 13970 ; 3 ; correct | 13970 ; 5 ; correct |
| C08 | 605580 | 605580 ; 2 ; correct | — ; 2 ; abstention |
| C09 | 487980 | 487980 ; 2 ; correct | 487980 ; 3 ; correct |
| C10 | 558980 | — ; 1 ; abstention | — ; 2 ; abstention |
| C11 | 446690 | 446690 ; 2 ; correct | 446690 ; 3 ; correct |
| C12 | 1666490 | 1666490 ; 3 ; correct | 1666490 ; 5 ; correct |
| C13 | 107740 | 107740 ; 3 ; correct | 107740 ; 5 ; correct |
| C14 | 0 | 0 ; 3 ; correct | 0 ; 5 ; correct |
| C15 | 168680 | 168680 ; 2 ; correct | 168680 ; 3 ; correct |
| C16 | 376740 | 376740 ; 2 ; correct | 376740 ; 3 ; correct |
| C17 | 258180 | — ; 1 ; abstention | 258180 ; 3 ; correct |
| C18 | 62480 | 62480 ; 3 ; correct | 62480 ; 4 ; correct |
| C19 | 1990 | — ; 1 ; abstention | 1990 ; 3 ; correct |
| C20 | 1106090 | 1106090 ; 3 ; correct | 1106090 ; 5 ; correct |

### Explication de chaque décision et différence de voix

Les valeurs sont en centimes. ∅ représente l’absence de valeur exécutable. Une voix supplémentaire ne suffit pas toujours : le seuil augmente également. Les statuts sont ceux du CSV, sans attribuer arbitrairement une cause réseau à une erreur SQL.

- **C01 — Décision inchangée** : 120B=792800 [correct]; Cohere=792800 [correct]; Qwen=∅ [sql_rejected]; Dots=792800 [correct]; 20B=792800 [correct]. Maximum de voix : 2 → 4 (seuil : 2 → 3).
- **C02 — Consensus perdu** : 120B=590320 [correct]; Cohere=∅ [sql_invalid]; Qwen=590320 [correct]; Dots=0 [incorrect]; 20B=0 [incorrect]. Maximum de voix : 2 → 2 (seuil : 2 → 3).
- **C03 — Décision inchangée** : 120B=936350 [correct]; Cohere=936350 [correct]; Qwen=936350 [correct]; Dots=936350 [correct]; 20B=936350 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C04 — Décision inchangée** : 120B=2826250 [correct]; Cohere=2826250 [correct]; Qwen=2826250 [correct]; Dots=2826250 [correct]; 20B=2826250 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C05 — Décision inchangée** : 120B=38480 [correct]; Cohere=38480 [correct]; Qwen=38480 [correct]; Dots=38480 [correct]; 20B=38480 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C06 — Décision inchangée** : 120B=0 [correct]; Cohere=0 [correct]; Qwen=0 [correct]; Dots=0 [correct]; 20B=0 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C07 — Décision inchangée** : 120B=13970 [correct]; Cohere=13970 [correct]; Qwen=13970 [correct]; Dots=13970 [correct]; 20B=13970 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C08 — Consensus perdu** : 120B=605580 [correct]; Cohere=0 [incorrect]; Qwen=605580 [correct]; Dots=25920 [incorrect]; 20B=25920 [incorrect]. Maximum de voix : 2 → 2 (seuil : 2 → 3).
- **C09 — Décision inchangée** : 120B=487980 [correct]; Cohere=0 [incorrect]; Qwen=487980 [correct]; Dots=0 [incorrect]; 20B=487980 [correct]. Maximum de voix : 2 → 3 (seuil : 2 → 3).
- **C10 — Décision inchangée** : 120B=558980 [correct]; Cohere=∅ [sql_invalid]; Qwen=119410 [incorrect]; Dots=0 [incorrect]; 20B=558980 [correct]. Maximum de voix : 1 → 2 (seuil : 2 → 3).
- **C11 — Décision inchangée** : 120B=446690 [correct]; Cohere=0 [incorrect]; Qwen=446690 [correct]; Dots=0 [incorrect]; 20B=446690 [correct]. Maximum de voix : 2 → 3 (seuil : 2 → 3).
- **C12 — Décision inchangée** : 120B=1666490 [correct]; Cohere=1666490 [correct]; Qwen=1666490 [correct]; Dots=1666490 [correct]; 20B=1666490 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C13 — Décision inchangée** : 120B=107740 [correct]; Cohere=107740 [correct]; Qwen=107740 [correct]; Dots=107740 [correct]; 20B=107740 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C14 — Décision inchangée** : 120B=0 [correct]; Cohere=0 [correct]; Qwen=0 [correct]; Dots=0 [correct]; 20B=0 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).
- **C15 — Décision inchangée** : 120B=168680 [correct]; Cohere=168680 [correct]; Qwen=0 [incorrect]; Dots=138920 [incorrect]; 20B=168680 [correct]. Maximum de voix : 2 → 3 (seuil : 2 → 3).
- **C16 — Décision inchangée** : 120B=376740 [correct]; Cohere=376740 [correct]; Qwen=367050 [incorrect]; Dots=1367540 [incorrect]; 20B=376740 [correct]. Maximum de voix : 2 → 3 (seuil : 2 → 3).
- **C17 — Consensus correct gagné** : 120B=258180 [correct]; Cohere=371990 [incorrect]; Qwen=248490 [incorrect]; Dots=258180 [correct]; 20B=258180 [correct]. Maximum de voix : 1 → 3 (seuil : 2 → 3).
- **C18 — Décision inchangée** : 120B=62480 [correct]; Cohere=62480 [correct]; Qwen=62480 [correct]; Dots=39580 [incorrect]; 20B=62480 [correct]. Maximum de voix : 3 → 4 (seuil : 2 → 3).
- **C19 — Consensus correct gagné** : 120B=1990 [correct]; Cohere=0 [incorrect]; Qwen=∅ [not_executed]; Dots=1990 [correct]; 20B=1990 [correct]. Maximum de voix : 1 → 3 (seuil : 2 → 3).
- **C20 — Décision inchangée** : 120B=1106090 [correct]; Cohere=1106090 [correct]; Qwen=1106090 [correct]; Dots=1106090 [correct]; 20B=1106090 [correct]. Maximum de voix : 3 → 5 (seuil : 2 → 3).

Les cinq modèles isolés obtiennent : 120B 20/20, Cohere 13/20, Qwen 14/20, Dots 12/20, 20B 18/20. [Comparaison exploitable en CSV](../kit-td1/evidence/comparison.csv).

## 2. Erreurs partagées et diagnostic SQL

Les 100 cellules finales contiennent quatre valeurs erronées partagées : C02 (0 : Dots, 20B), C08 (25920 : Dots, 20B), C09 (0 : Cohere, Dots), C11 (0 : Cohere, Dots). Aucun de ces accords ne remporte un quorum erroné. C02/C08 font cependant s’abstenir 3/5. [Inventaire complet avec SQL et votes](../kit-td1/evidence/shared-wrong-values.json).

**Cas analysé : C08, issu des traces réelles, sans recourir au cas historique DEMO-SQL-C11.** Les deux modèles confondent l’âge révolu avec l’anniversaire exact. Le [diagnostic complet](td2-diagnostic-c08.md) contient leurs deux requêtes intégrales, la référence, la requête delta exécutée et les clients responsables de chacun des 579 660 centimes manquants. Référence : 605580 ; réponses fautives : 25920 ; 2/3 correct avec 2 voix, 3/5 abstention avec 2 voix maximum.

## 3. Règle de routage et simulateur

La [règle d’une page](td2-regle-routage.md) précise les ratios, cellules, modèles et contrôles pour chaque famille et les trois usages. Tous les modèles du lot sont sur une route gratuite ; à égalité, nous choisissons un modèle à 100 % sur la famille, puis l’identifiant lexical. 120B est retenu ici pour toutes les familles. Cette règle est une hypothèse locale, pas un classement permanent.

| Famille | Cellules | 120B | Cohere | Qwen | Dots | 20B |
|---|---|---:|---:|---:|---:|---:|
| F1 | C01, C04, C05, C06, C07, C20 | 6/6 | 6/6 | 5/6 | 6/6 | 6/6 |
| F2 | C02, C08, C09, C11 | 4/4 | 0/4 | 4/4 | 0/4 | 2/4 |
| F2b | C10 | 1/1 | 0/1 | 0/1 | 0/1 | 1/1 |
| F3 | C12 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| F1+F3 | C03, C13, C14 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| F1+F2 | C15 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 |
| F2+F3 | C16 | 1/1 | 1/1 | 0/1 | 0/1 | 1/1 |
| F1+F2+F3 | C17, C19 | 2/2 | 0/2 | 0/2 | 2/2 | 2/2 |
| F1+F2b | C18 | 1/1 | 1/1 | 1/1 | 0/1 | 1/1 |

| Scénario | Avant : action / ressource | Après : action / ressource / contrôle |
|---|---|---|
| simple | run / small-free | run / groq:openai/gpt-oss-120b / none |
| complex | run / senior-subscription | run / groq:openai/gpt-oss-120b / none |
| deferrable | defer / senior-subscription | defer / groq:openai/gpt-oss-120b / none |
| urgent | run / senior-api | abstain / None / reference |
| budget exhausted | abstain / None | abstain / None / reference |
| high impact | run / senior-subscription | run / groq:openai/gpt-oss-120b / reference + human review |
| unknown capability | abstain / None | abstain / None / reference |

Avant : ressources fictives du script fourni. Après : les cinq routes TD1 réelles, avec disponibilités toujours simulées. Les scénarios de pénurie épuisent maintenant ces cinq routes ; cela explique que le scénario urgent s’abstienne au lieu d’inventer un modèle payant mesuré. Chaque `reason` cite les cellules de la famille et le ratio du modèle, ou tous les ratios si aucune route ne convient. [Avant](../kit-td1/evidence/routage-avant.jsonl), [après](../kit-td1/evidence/routage-apres.jsonl), [27 décisions familles × usages](../kit-td1/evidence/routage-familles-usages.json).

### Pourquoi l’abonnement disponible précède le report

Dans le code initial, le bloc `included` s’exécute et retourne avant le bloc `waiting`. Une ressource immédiatement disponible avec `cash == 0` est incluse même si son `allocation > 0` ; le tri par allocation n’a lieu qu’entre les ressources déjà disponibles. Une route gratuite épuisée n’entre donc pas dans ce premier tri. La règle privilégie le service immédiat sans nouvelle dépense.

Inverser cette priorité est justifié si la demande tolère réellement le délai de refill et si l’on veut réserver une allocation d’abonnement rare à des demandes urgentes futures. Le budget d’opportunité, et pas seulement le cash, motive ce choix. Le paramètre `preserve_subscription` implémente cette option ; il ne retarde pas une route gratuite déjà disponible. Le refill doit rester dans le délai et la disponibilité doit être revérifiée au réveil.

## 4. Reproduction et validation

Depuis la racine du dépôt, avec Python ≥ 3.10, bibliothèque standard uniquement :

```bash
cd kit-td1
python -m unittest -v test_td2.py
python analyse_td2.py
python atelier-routage.py --scenario deferrable
```

Les 17 tests exécutés passent. Ils couvrent les majorités, doublons, erreurs, zéro, quorums 3/5, disponibilité, délais, budget, contrôle client/paiement et priorité d’allocation. Le script régénère les tableaux et preuves, vérifie les références et rapproche le delta SQL. Aucune clé ni réseau requis.

## 5. Limites, contributions et suite

Succès : code de vote, vingt comparaisons, quatre erreurs partagées repérées, diagnostic C08 réconcilié, règle fondée sur les taux et simulation avant/après. Difficultés observées : erreurs SQL et sorties non exécutées ; C10 reste sans majorité correcte. Corrélation possible entre modèles, petits effectifs (parfois un seul cas), disponibilité fictive et précision estimée sur le même lot limitent la généralisation.

Les prompts employés pour appeler les cinq modèles en TD1 n’ont pas changé : aucun appel en TD2. L’assistance de développement est documentée dans [td2-ai-assistance.md](td2-ai-assistance.md).

Répartition communiquée par le groupe : un trinôme et deux binômes.

| Équipe | Membres | Partie attribuée |
|---|---|---|
| A — trinôme | Yanice Hennouche, Roman Pons-Bouregba, Jawed Ferhat | Vote k sur n et comparaison des quorums 2/3 et 3/5 sur les vingt questions |
| B — binôme | Alvina Simon, Hugo Maitrehenry | Analyse de la valeur erronée partagée et diagnostic SQL du cas C08 |
| C — binôme | Badis Hamouri, Fatima Imghi | Taux par famille, règle de routage et adaptation du simulateur |

L’assistant a préparé le code, les calculs et ce rapport. Chaque équipe prend en charge la compréhension et la vérification de sa partie, puis l’explique aux autres. La réalisation de la revue croisée reste à renseigner par le groupe.

À faire par le groupe : relire et expliquer le code et le diagnostic, documenter la revue croisée, puis déposer l’URL du dépôt, le hash complet du commit et le lien du rapport à ce commit sur Moodle avant le **22 novembre 2026 à 23:59, heure de Paris**. Le dépôt Moodle reste à effectuer.

Énoncé suivi : [TD2, version du 18 novembre](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td2-en.html).
