# Règle de routage

F1 : période ; F2 : âge à date fixe ; F2b : âge à la commande ; F3 : produits.
Les combinaisons sont évaluées séparément. Les rapports correct/cas comptent
les erreurs techniques comme des échecs.

| Famille | Questions | 120B | Cohere | Qwen | Dots | 20B |
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

Les cinq routes TD1 sont gratuites. Le portefeuille indique 0 pour les trois
routes Groq ; Cohere et Dots utilisent les identifiants `:free` du kit actualisé.
À prix égal, on préfère un modèle à 100 % sur la famille, puis l'identifiant dans
l'ordre alphabétique. Avec ce lot, le premier modèle est donc 120B pour chaque famille.

| Usage | Contrôle |
|---|---|
| Tableau interne à faible enjeu | Aucun si le modèle choisi est à 100 % sur la famille ; sinon référence SQL |
| Chiffre montré au client | Référence SQL obligatoire |
| Paiement | Référence SQL et revue humaine obligatoires |

Un modèle reçoit le niveau 3 s'il a tout réussi sur la famille, 1 s'il a au moins
un succès sur une famille entièrement mesurée, sinon 0. Une demande complexe
exige le niveau 3. Ces niveaux ne valent que pour ce lot.

Si le premier modèle est indisponible : autre modèle éligible disponible,
sinon attente du refill si le délai le permet, sinon route payante mesurée dans
le budget, sinon abstention. Le lot ne contient aucune route payante mesurée.
La disponibilité est revérifiée au réveil.

Une référence absente, un désaccord ou une revue refusée bloque l'affichage ou
le paiement. `run` signifie lancer une proposition, pas autoriser un paiement.
Nous gardons un contrôle déterministe pour les usages à enjeu : un quorum peut
se tromper. Les taux sur vingt questions ne garantissent pas les résultats futurs.
