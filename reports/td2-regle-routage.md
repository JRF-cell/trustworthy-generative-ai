# TD2 — règle de routage

Les cinq routes du protocole TD1 sont gratuites à l’appel. Les trois routes Groq sont à 0 dans le portefeuille fourni ; Cohere et Dots sont les routes `:free` de la sélection actualisée du kit, absentes du CSV de portefeuille ancien. Aucun prix payant ni abonnement n’est inventé. À prix égal : préférer 100 % observé sur la famille, puis l’identifiant complet dans l’ordre lexical. Cela sélectionne 120B dans ce lot.

Ratios exacts correct/cas, erreurs techniques incluses dans le dénominateur. F1 = période, F2 = âge à date fixe, F2b = âge à la commande, F3 = produits. Les combinaisons sont séparées ; C03/C13/C14 sont F1+F3.

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

| Usage | Premier modèle | Vérification obligatoire |
|---|---|---|
| Tableau interne, faible enjeu | 120B ; ratio de la famille ci-dessus | none seulement si le modèle choisi est à 100 % sur cette famille ; sinon référence déterministe |
| Chiffre présenté au client | 120B | référence déterministe, indépendamment du ratio |
| Montant payé | 120B | référence déterministe + revue humaine avant paiement |

Une route avec au moins un succès et une famille complètement mesurée reçoit le niveau 1 ; une route à 100 % reçoit le niveau 3 ; zéro succès ou données manquantes donnent le niveau 0. Ces niveaux décrivent cette politique locale, pas une intelligence générale. Une demande complexe exige le niveau 3. Une route de niveau 1 reste utilisable pour une demande simple, avec référence obligatoire.

Indisponibilité : autre modèle éligible disponible à coût minimal ; sinon attendre le refill si le délai le permet ; sinon route payante mesurée dans le budget (aucune dans ce lot) ; sinon abstention. Vérifier à nouveau la disponibilité au réveil. Une référence absente, un désaccord avec elle, ou une revue refusée interdit de publier/payer : revue ou abstention. `run` lance une proposition à contrôler, pas une autorisation de paiement.

Les quorums 2/3 et 3/5 sont mesurés dans le rapport. La règle de service retient la vérification déterministe, car 3/5 ne domine pas 2/3 sur ce lot. Pour un domaine sans référence, demander une revue et s’abstenir tant qu’elle n’est pas concluante. Vingt cas ne constituent pas une garantie future.
