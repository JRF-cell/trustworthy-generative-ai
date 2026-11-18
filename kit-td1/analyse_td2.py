"""Reproduce all TD2 evidence from stored real traces, without network calls."""
import csv
import hashlib
import json
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from build_references import read_csv, independent_csv_total, SPECS
from td2_common import HERE, PANEL3, PANEL5, FAMILIES, load_cells, proposals, vote, rates, load_module

REPORTS = HERE.parent / 'reports'
ALIASES = dict(zip(PANEL5, ['120B', 'Cohere', 'Qwen', 'Dots', '20B']))


def dump_json(name, data):
    (HERE / 'evidence' / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def dump_csv(name, data):
    with (HERE / 'evidence' / name).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def capture(script, filename):
    result = subprocess.run([sys.executable, str(HERE / script)], cwd=HERE,
                            capture_output=True, text=True, encoding='utf-8', check=True)
    (HERE / 'evidence' / filename).write_text(result.stdout, encoding='utf-8')
    return result.stdout


def main():
    capture('verify-data.py', 'data-check-before.json')
    ref_rows = read_csv(HERE / 'reference-td1.csv')
    refs = {r['case_id']: int(r['revenue_cents']) for r in ref_rows}
    if set(refs) != {f'C{i:02}' for i in range(1, 21)}:
        raise ValueError('Expected the twenty independent TD1 references')
    cells = load_cells(HERE / 'traces-td1.csv', 'real', refs)
    if len(cells) != 100:
        raise ValueError(f'Incomplete observations: {len(cells)}/100')
    raw = read_csv(HERE / 'traces-td1.csv')
    # Validate the group's references independently without rewriting them.
    checks = []
    with sqlite3.connect((HERE / 'data/boutique.sqlite').as_uri() + '?mode=ro', uri=True) as con:
        for row in ref_rows:
            case = row['case_id']
            actual = con.execute(row['sql']).fetchone()[0]
            independent = independent_csv_total(SPECS[case])
            if actual != refs[case] or actual != independent:
                raise ValueError(f'Reference disagreement: {case}')
            checks.append(dict(case_id=case, sql_cents=actual, independent_csv_cents=independent, ok=True))
    dump_csv('reference-check.csv', checks)
    dump_json('provenance.json', dict(
        source_repo='https://github.com/JRF-cell/trustworthy-generative-ai',
        source_commit='3dc2201cf55a7ab6e83b5134431127df18c0bb63',
        trace_rows=len(raw), final_cells=len(cells), nature='real',
        selection='last CSV row for each provider/model/case, same as atelier-vote.py',
        sha256={f: hashlib.sha256((HERE / f).read_bytes()).hexdigest()
                for f in ['traces-td1.csv', 'reference-td1.csv', 'data/boutique.sqlite']}))

    comparison, wrong = [], []
    summary = {'2of3': Counter(), '3of5': Counter()}
    table = ['| Cas | Référence | 2/3 : valeur ; voix ; verdict | 3/5 : valeur ; voix ; verdict |',
             '|---|---:|---|---|']
    details = []
    for case, ref in sorted(refs.items()):
        record = dict(case=case, reference=ref)
        results, displayed = [], []
        for label, panel, k in [('2of3', PANEL3, 2), ('3of5', PANEL5, 3)]:
            result = vote(proposals(cells, case, panel), k)
            verdict = 'abstention' if not result['consensus'] else ('correct' if result['value'] == ref else 'incorrect')
            summary[label][verdict] += 1
            record[label] = result
            results.append(result)
            displayed.append(f"{result['value'] if result['consensus'] else '—'} ; {result['votes']} ; {verdict}")
        table.append(f"| {case} | {ref} | {' | '.join(displayed)} |")
        observations = '; '.join(f"{ALIASES[p,m]}={cells[case,p,m]['value'] or '∅'} [{cells[case,p,m]['verdict']}]"
                                 for p,m in PANEL5)
        record['observations'] = observations
        comparison.append(record)
        a,b = results
        if (a['consensus'], a['value']) != (b['consensus'], b['value']):
            change = 'Consensus perdu' if not b['consensus'] else 'Consensus correct gagné'
        else:
            change = 'Décision inchangée'
        details += [f"- **{case} — {change}** : {observations}. Maximum de voix : {a['votes']} → {b['votes']} (seuil : 2 → 3)."]
        groups = defaultdict(list)
        for p,m in PANEL5:
            r = cells[case,p,m]
            if r['verdict'] == 'incorrect':
                groups[int(r['value'])].append(dict(provider=p, model=m, sql=r['sql']))
        for value, members in groups.items():
            if len(members) >= 2:
                wrong.append(dict(case=case, value=value, reference=ref, models=members,
                                  vote2=a, vote5=b))
    dump_json('comparison.json', comparison)
    dump_csv('comparison.csv', [dict(case=r['case'], reference=r['reference'],
        vote_2of3=json.dumps(r['2of3']), vote_3of5=json.dumps(r['3of5']),
        observations=r['observations']) for r in comparison])
    dump_json('shared-wrong-values.json', wrong)
    dump_json('vote-summary.json', summary)

    stats = rates(cells)
    dump_json('family-rates.json', stats)
    rate_table = ['| Famille | Cellules | 120B | Cohere | Qwen | Dots | 20B |',
                  '|---|---|---:|---:|---:|---:|---:|']
    for family, cases in FAMILIES.items():
        group = [s for s in stats if s['family'] == family]
        rate_table.append(f"| {family} | {', '.join(cases)} | " + ' | '.join(f"{s['correct']}/{s['total']}" for s in group) + ' |')

    # C08 is a real shared wrong value. Re-execute both stored SQL queries.
    faulty = [cells['C08', *PANEL5[i]] for i in [3,4]]
    delta_sql = (HERE / 'sql/c08_delta.sql').read_text(encoding='utf-8')
    with sqlite3.connect((HERE / 'data/boutique.sqlite').as_uri() + '?mode=ro', uri=True) as con:
        con.row_factory = sqlite3.Row
        delta = [dict(r) for r in con.execute(delta_sql)]
        values = [con.execute(r['sql']).fetchone()[0] for r in faulty]
    if values != [25920,25920] or sum(r['missed_revenue_cents'] for r in delta) != refs['C08'] - 25920:
        raise ValueError('C08 delta did not reconcile')
    dump_csv('c08-delta.csv', delta)
    dump_json('c08-results.json', dict(faulty_values=values, reference=refs['C08'],
                                     missed_cents=sum(r['missed_revenue_cents'] for r in delta)))
    for name, row in zip(['dots', '20b'], faulty):
        (HERE / 'sql' / f'c08_{name}.sql').write_text(row['sql'] + '\n', encoding='utf-8')
    reference_sql = next(r['sql'] for r in ref_rows if r['case_id'] == 'C08')
    (HERE / 'sql/c08_reference.sql').write_text(reference_sql + '\n', encoding='utf-8')
    diagnostic = ['# Diagnostic C08 — valeur erronée partagée dans les traces réelles', '',
        'Dots et GPT-OSS 20B renvoient **25 920 centimes**, contre **605 580** pour la référence. Les deux requêtes ont été réexécutées sur la base du groupe. Écart : **579 660 centimes (5 796,60 €)**.', '',
        '## Votes comptés à la main et vérifiés par le code', '',
        '- Panel fixe 2/3 : 120B = 605580, Cohere = 0, Qwen = 605580. Consensus correct, deux voix.',
        '- Panel 3/5 : les trois mêmes, plus Dots = 25920 et 20B = 25920. Deux voix pour 605580, deux pour 25920, une pour 0 : abstention, maximum deux voix.',
        '- La valeur erronée partagée ne gagne aucun des deux quorums. Dots et 20B sont tous deux hors du panel fixe ; leur ajout supprime ici un consensus correct.', '',
        '## Cause SQL', '',
        'Les personnes de 25 ans révolus le 24 septembre 2026 sont nées dans **]2000-09-24, 2001-09-24]**. Les deux modèles ne sélectionnent que la naissance du **24 septembre 2001** : ils confondent « avoir 25 ans » et « fêter son 25e anniversaire ce jour-là ». Dots exige séparément l’année 2001, le mois 09 et le jour 24. 20B emploie la fenêtre d’un seul jour [2001-09-24, 2001-09-25[. Pour les dates ISO présentes, les deux prédicats sont équivalents.', '',
        'Les JOIN et le calcul quantité × prix sont corrects ; la cause est le WHERE sur la naissance. Aucune borne sur la date des commandes n’est demandée : toutes leurs commandes comptent.', '']
    for title, sql in [('Dots — SQL complet', faulty[0]['sql']), ('20B — SQL complet', faulty[1]['sql']),
                       ('Référence du groupe', reference_sql), ('Diagnostic des lignes omises', delta_sql)]:
        diagnostic += [f'## {title}', '', '```sql', sql.strip(), '```', '']
    diagnostic += ['| Client omis | Naissance | CA HT omis, centimes |', '|---|---|---:|']
    diagnostic += ['| ' + ' | '.join(str(v) for v in row.values()) + ' |' for row in delta]
    diagnostic += ['', '**Total omis : 579 660.** Le client né le 24/09/2001 reste inclus pour 25 920 ; 25 920 + 579 660 = 605 580. Les requêtes fautives ajoutent zéro client hors référence.', '',
        'Vérification indépendante : jointure des CSV en Python, calcul de l’âge par différence des années puis retrait de 1 si l’anniversaire n’est pas encore passé. Le total vaut aussi 605 580. Voir `evidence/reference-check.csv` et `build_references.py`.', '',
        'Conséquence : augmenter n ne garantit ni plus de couverture ni plus de justesse. Pour un résultat client ou un paiement, vérifier déterministement les conditions d’âge. Le consensus n’est jamais une preuve SQL.']
    (REPORTS / 'td2-diagnostic-c08.md').write_text('\n'.join(diagnostic) + '\n', encoding='utf-8')

    vote_examples = capture('atelier-vote.py', 'vote-synthetique.jsonl')
    before = [json.loads(s) for s in capture('original/atelier-routage.py', 'routage-avant.jsonl').splitlines()]
    after = [json.loads(s) for s in capture('atelier-routage.py', 'routage-apres.jsonl').splitlines()]
    with sqlite3.connect(':memory:') as con:
        con.execute('CREATE TABLE sale(sale_date TEXT, amount_cents INTEGER)')
        con.execute("INSERT INTO sale VALUES ('2026-01-01', 100)")
        toy = {op: con.execute(f"SELECT COALESCE(SUM(amount_cents),0) FROM sale WHERE sale_date {op} '2026-01-01' AND sale_date < '2026-01-02'").fetchone()[0] for op in ['>', '>=']}
    dump_json('demo-vote-boundary.json', dict(nature='synthetic toy SQL', results=toy))

    router = load_module('td2_router_report', HERE / 'atelier-routage.py')
    resources = router.measured_resources()
    rule = ['# TD2 — règle de routage', '',
        'Les cinq routes du protocole TD1 sont gratuites à l’appel. Les trois routes Groq sont à 0 dans le portefeuille fourni ; Cohere et Dots sont les routes `:free` de la sélection actualisée du kit, absentes du CSV de portefeuille ancien. Aucun prix payant ni abonnement n’est inventé. À prix égal : préférer 100 % observé sur la famille, puis l’identifiant complet dans l’ordre lexical. Cela sélectionne 120B dans ce lot.', '',
        'Ratios exacts correct/cas, erreurs techniques incluses dans le dénominateur. F1 = période, F2 = âge à date fixe, F2b = âge à la commande, F3 = produits. Les combinaisons sont séparées ; C03/C13/C14 sont F1+F3.', '', *rate_table, '',
        '| Usage | Premier modèle | Vérification obligatoire |', '|---|---|---|',
        '| Tableau interne, faible enjeu | 120B ; ratio de la famille ci-dessus | none seulement si le modèle choisi est à 100 % sur cette famille ; sinon référence déterministe |',
        '| Chiffre présenté au client | 120B | référence déterministe, indépendamment du ratio |',
        '| Montant payé | 120B | référence déterministe + revue humaine avant paiement |', '',
        'Une route avec au moins un succès et une famille complètement mesurée reçoit le niveau 1 ; une route à 100 % reçoit le niveau 3 ; zéro succès ou données manquantes donnent le niveau 0. Ces niveaux décrivent cette politique locale, pas une intelligence générale. Une demande complexe exige le niveau 3. Une route de niveau 1 reste utilisable pour une demande simple, avec référence obligatoire.', '',
        'Indisponibilité : autre modèle éligible disponible à coût minimal ; sinon attendre le refill si le délai le permet ; sinon route payante mesurée dans le budget (aucune dans ce lot) ; sinon abstention. Vérifier à nouveau la disponibilité au réveil. Une référence absente, un désaccord avec elle, ou une revue refusée interdit de publier/payer : revue ou abstention. `run` lance une proposition à contrôler, pas une autorisation de paiement.', '',
        'Les quorums 2/3 et 3/5 sont mesurés dans le rapport. La règle de service retient la vérification déterministe, car 3/5 ne domine pas 2/3 sur ce lot. Pour un domaine sans référence, demander une revue et s’abstenir tant qu’elle n’est pas concluante. Vingt cas ne constituent pas une garantie future.']
    (REPORTS / 'td2-regle-routage.md').write_text('\n'.join(rule) + '\n', encoding='utf-8')
    family_decisions = []
    for family in FAMILIES:
        for use in ['internal', 'customer', 'payout']:
            request = dict(family=family, use=use, difficulty=1, can_wait=True, deadline_minutes=120, budget=0)
            family_decisions.append(dict(request=request, result=router.choose(request, resources)))
    dump_json('routage-familles-usages.json', family_decisions)

    routing_table = ['| Scénario | Avant : action / ressource | Après : action / ressource / contrôle |', '|---|---|---|']
    for a,b in zip(before, after):
        x,y = a['result'],b['result']
        routing_table.append(f"| {a['scenario']} | {x['action']} / {x['resource']} | {y['action']} / {y['resource']} / {y['checks']} |")
    totals = {ALIASES[p,m]: sum(cells[c,p,m]['verdict'] == 'correct' for c in refs) for p,m in PANEL5}
    report = ['# TD2 — Le quorum, puis la règle de routage', '',
        '**DIA 5 — sous-groupe 2 · 18 novembre 2026**', '',
        '## Résultat', '',
        'Sur les 20 questions, **2/3 et 3/5 produisent chacun 17 consensus corrects, 0 consensus erroné et 3 abstentions**. Leur couverture est de 85 %, et leur exactitude conditionnelle sur les consensus de 17/17. Ces proportions décrivent uniquement ce lot.', '',
        '**3/5 perd les réponses correctes de C02 et C08, mais résout C17 et C19. C10 reste une abstention.** Les modèles peuvent partager une même erreur SQL : le cas réel C08 est démontré avec les clients omis et un écart exact de 579 660 centimes.', '',
        '## Provenance et méthode', '',
        'Dépôt source : [JRF-cell/trustworthy-generative-ai](https://github.com/JRF-cell/trustworthy-generative-ai), commit initial `3dc2201cf55a7ab6e83b5134431127df18c0bb63`. Entrées : [traces TD1](../kit-td1/traces-td1.csv), [références TD1](../kit-td1/reference-td1.csv). Le CSV contient 103 tentatives, ramenées aux 100 cellules finales par la dernière ligne pour chaque fournisseur/modèle/question, comme dans l’atelier fourni. Nature : `real`. Aucun nouvel appel de modèle.', '',
        'La base et les trois CSV passent la vérification d’intégrité avant et après. Les 20 requêtes de référence du groupe ont été exécutées en lecture seule puis contrôlées par un calcul Python indépendant sur les CSV. Les références historiques et les traces sont conservées inchangées. [Preuves de provenance](../kit-td1/evidence/provenance.json), [double vérification](../kit-td1/evidence/reference-check.csv).', '',
        'Les trois tentatives supplémentaires concernent Qwen : C17 passe de `not_executed` à `incorrect`, C18 de `not_executed` à `correct`, C19 reste `not_executed`. Les dates sont conservées telles qu’exportées ; la sélection suit l’ordre du CSV. Les documents TD1 narratifs du dépôt sont antérieurs aux résultats et n’ont pas été réécrits.', '',
        'Sous Windows, Git avait converti les fins de ligne des CSV et du schéma en CRLF, modifiant leurs empreintes sans changer les données. Les fins de ligne officielles LF ont été rétablies ; `.gitattributes` les préserve pour les futurs clones. Les empreintes correspondent désormais toutes au manifeste officiel.', '',
        '## 1. Vote k sur n', '',
        'La méthode [vote_k_sur_n](../kit-td1/skeleton-multi-llm-en.py) valide n//2 < k ≤ n et l’unicité des couples fournisseur/modèle avant tout résultat. Seules les propositions exécutées avec une valeur entière votent. Une indisponibilité conserve sa place dans n. Aucun verdict de justesse ni référence n’est transmis au vote ; la comparaison intervient ensuite.', '',
        'Panel fixe : 120B = `groq:openai/gpt-oss-120b`, Cohere = `openrouter:cohere/north-mini-code:free`, Qwen = `groq:qwen/qwen3.8-27b`. Le quorum 3/5 ajoute Dots = `openrouter:dots-studio/dots-3-note-preview:free` et 20B = `groq:openai/gpt-oss-20b`. Attention : 120B et 20B appartiennent à la même famille GPT-OSS ; cinq modèles ne signifient pas cinq erreurs indépendantes.', '',
        'Quatre exemples synthétiques exécutés : accord [100,100,120] → 100 (2 voix) ; désaccord [100,110,120] → abstention (1) ; indisponibles [100,None,None] → abstention (1) ; mauvais consensus [0,0,100] → 0 (2), malgré la référence 100. La table jouet confirme `>` → 0 et `>=` → 100 sur la vente du 01/01/2026. [Sorties](../kit-td1/evidence/vote-synthetique.jsonl).', '',
        *table, '',
        '### Explication de chaque décision et différence de voix', '',
        'Les valeurs sont en centimes. ∅ représente l’absence de valeur exécutable. Une voix supplémentaire ne suffit pas toujours : le seuil augmente également. Les statuts sont ceux du CSV, sans attribuer arbitrairement une cause réseau à une erreur SQL.', '',
        *details, '',
        'Les cinq modèles isolés obtiennent : ' + ', '.join(f'{m} {n}/20' for m,n in totals.items()) + '. [Comparaison exploitable en CSV](../kit-td1/evidence/comparison.csv).', '',
        '## 2. Erreurs partagées et diagnostic SQL', '',
        'Les 100 cellules finales contiennent quatre valeurs erronées partagées : C02 (0 : Dots, 20B), C08 (25920 : Dots, 20B), C09 (0 : Cohere, Dots), C11 (0 : Cohere, Dots). Aucun de ces accords ne remporte un quorum erroné. C02/C08 font cependant s’abstenir 3/5. [Inventaire complet avec SQL et votes](../kit-td1/evidence/shared-wrong-values.json).', '',
        '**Cas analysé : C08, issu des traces réelles, sans recourir au cas historique DEMO-SQL-C11.** Les deux modèles confondent l’âge révolu avec l’anniversaire exact. Le [diagnostic complet](td2-diagnostic-c08.md) contient leurs deux requêtes intégrales, la référence, la requête delta exécutée et les clients responsables de chacun des 579 660 centimes manquants. Référence : 605580 ; réponses fautives : 25920 ; 2/3 correct avec 2 voix, 3/5 abstention avec 2 voix maximum.', '',
        '## 3. Règle de routage et simulateur', '',
        'La [règle d’une page](td2-regle-routage.md) précise les ratios, cellules, modèles et contrôles pour chaque famille et les trois usages. Tous les modèles du lot sont sur une route gratuite ; à égalité, nous choisissons un modèle à 100 % sur la famille, puis l’identifiant lexical. 120B est retenu ici pour toutes les familles. Cette règle est une hypothèse locale, pas un classement permanent.', '',
        *rate_table, '',
        *routing_table, '',
        'Avant : ressources fictives du script fourni. Après : les cinq routes TD1 réelles, avec disponibilités toujours simulées. Les scénarios de pénurie épuisent maintenant ces cinq routes ; cela explique que le scénario urgent s’abstienne au lieu d’inventer un modèle payant mesuré. Chaque `reason` cite les cellules de la famille et le ratio du modèle, ou tous les ratios si aucune route ne convient. [Avant](../kit-td1/evidence/routage-avant.jsonl), [après](../kit-td1/evidence/routage-apres.jsonl), [27 décisions familles × usages](../kit-td1/evidence/routage-familles-usages.json).', '',
        '### Pourquoi l’abonnement disponible précède le report', '',
        'Dans le code initial, le bloc `included` s’exécute et retourne avant le bloc `waiting`. Une ressource immédiatement disponible avec `cash == 0` est incluse même si son `allocation > 0` ; le tri par allocation n’a lieu qu’entre les ressources déjà disponibles. Une route gratuite épuisée n’entre donc pas dans ce premier tri. La règle privilégie le service immédiat sans nouvelle dépense.', '',
        'Inverser cette priorité est justifié si la demande tolère réellement le délai de refill et si l’on veut réserver une allocation d’abonnement rare à des demandes urgentes futures. Le budget d’opportunité, et pas seulement le cash, motive ce choix. Le paramètre `preserve_subscription` implémente cette option ; il ne retarde pas une route gratuite déjà disponible. Le refill doit rester dans le délai et la disponibilité doit être revérifiée au réveil.', '',
        '## 4. Reproduction et validation', '',
        'Depuis la racine du dépôt, avec Python ≥ 3.10, bibliothèque standard uniquement :', '',
        '```bash', 'cd kit-td1', 'python -m unittest -v test_td2.py', 'python analyse_td2.py', 'python atelier-routage.py --scenario deferrable', '```', '',
        'Les 17 tests exécutés passent. Ils couvrent les majorités, doublons, erreurs, zéro, quorums 3/5, disponibilité, délais, budget, contrôle client/paiement et priorité d’allocation. Le script régénère les tableaux et preuves, vérifie les références et rapproche le delta SQL. Aucune clé ni réseau requis.', '',
        '## 5. Limites, contributions et suite', '',
        'Succès : code de vote, vingt comparaisons, quatre erreurs partagées repérées, diagnostic C08 réconcilié, règle fondée sur les taux et simulation avant/après. Difficultés observées : erreurs SQL et sorties non exécutées ; C10 reste sans majorité correcte. Corrélation possible entre modèles, petits effectifs (parfois un seul cas), disponibilité fictive et précision estimée sur le même lot limitent la généralisation.', '',
        'Les prompts employés pour appeler les cinq modèles en TD1 n’ont pas changé : aucun appel en TD2. L’assistance de développement est documentée dans [td2-ai-assistance.md](td2-ai-assistance.md).', '',
        'Répartition communiquée par le groupe : un trinôme et deux binômes.', '',
        '| Équipe | Membres | Partie attribuée |', '|---|---|---|',
        '| A — trinôme | Yanice Hennouche, Roman Pons-Bouregba, Jawed Ferhat | Vote k sur n et comparaison des quorums 2/3 et 3/5 sur les vingt questions |',
        '| B — binôme | Alvina Simon, Hugo Maitrehenry | Analyse de la valeur erronée partagée et diagnostic SQL du cas C08 |',
        '| C — binôme | Badis Hamouri, Fatima Imghi | Taux par famille, règle de routage et adaptation du simulateur |', '',
        'L’assistant a préparé le code, les calculs et ce rapport. Chaque équipe prend en charge la compréhension et la vérification de sa partie, puis l’explique aux autres. La réalisation de la revue croisée reste à renseigner par le groupe.', '',
        'À faire par le groupe : relire et expliquer le code et le diagnostic, documenter la revue croisée, puis déposer l’URL du dépôt, le hash complet du commit et le lien du rapport à ce commit sur Moodle avant le **22 novembre 2026 à 23:59, heure de Paris**. Le dépôt Moodle reste à effectuer.', '',
        'Énoncé suivi : [TD2, version du 18 novembre](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td2-en.html).']
    (REPORTS / 'td2.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    capture('verify-data.py', 'data-check-after.json')
    print(json.dumps(dict(cells=len(cells), shared_wrong_cases=len(wrong), summary=summary,
                          c08_delta=sum(r['missed_revenue_cents'] for r in delta)), indent=2))


if __name__ == '__main__':
    main()
