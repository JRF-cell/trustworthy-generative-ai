"""TD2 : comparer les votes, vérifier C08 et enregistrer les simulations."""
import csv
import json
import sqlite3
import subprocess
import sys
from td2_common import HERE, PANEL3, PANEL5, FAMILIES, read_csv, load_cells, proposals, vote, rates, load_module
from verification_csv import SPECS, independent_csv_total


def save_json(name, data):
    (HERE / 'evidence' / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def save_csv(name, rows):
    with (HERE / 'evidence' / name).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_script(script, output):
    result = subprocess.run([sys.executable, str(HERE / script)], cwd=HERE,
                            capture_output=True, text=True, encoding='utf-8', check=True)
    (HERE / 'evidence' / output).write_text(result.stdout, encoding='utf-8')


def compare_votes(cells, references):
    comparison, wrong, csv_rows = [], [], []
    summary = {'2of3': {}, '3of5': {}}
    aliases = ['120B', 'Cohere', 'Qwen', 'Dots', '20B']
    for case, reference in sorted(references.items()):
        row = {'case': case, 'reference': reference}
        for label, panel, k in [('2of3', PANEL3, 2), ('3of5', PANEL5, 3)]:
            result = vote(proposals(cells, case, panel), k)
            if not result['consensus']:
                verdict = 'abstention'
            elif result['value'] == reference:
                verdict = 'correct'
            else:
                verdict = 'incorrect'
            summary[label][verdict] = summary[label].get(verdict, 0) + 1
            row[label] = result
        observations = []
        wrong_values = {}
        for (provider, model), alias in zip(PANEL5, aliases):
            cell = cells[case, provider, model]
            observations.append(f"{alias}={cell['value'] or '∅'} [{cell['verdict']}]")
            if cell['verdict'] == 'incorrect':
                member = {'provider': provider, 'model': model, 'sql': cell['sql']}
                wrong_values.setdefault(int(cell['value']), []).append(member)
        row['observations'] = '; '.join(observations)
        comparison.append(row)
        csv_rows.append({'case': case, 'reference': reference,
                         'vote_2of3': json.dumps(row['2of3']), 'vote_3of5': json.dumps(row['3of5']),
                         'observations': row['observations']})
        for value, models in wrong_values.items():
            if len(models) >= 2:
                wrong.append({'case': case, 'value': value, 'reference': reference,
                              'models': models, 'vote2': row['2of3'], 'vote5': row['3of5']})
    save_csv('comparison.csv', csv_rows)
    save_json('comparison.json', comparison)
    save_json('vote-summary.json', summary)
    save_json('shared-wrong-values.json', wrong)
    save_json('family-rates.json', rates(cells))
    print('Résultats des votes :', summary)
    print('Valeurs erronées partagées :', len(wrong))


def check_sql(cells, reference_rows):
    checks = []
    db = (HERE / 'data/boutique.sqlite').as_uri() + '?mode=ro'
    with sqlite3.connect(db, uri=True) as con:
        con.row_factory = sqlite3.Row
        for row in reference_rows:
            case = row['case_id']
            sql_value = con.execute(row['sql']).fetchone()[0]
            csv_value = independent_csv_total(SPECS[case])
            if sql_value != csv_value or sql_value != int(row['revenue_cents']):
                raise ValueError(f'Référence à vérifier : {case}')
            checks.append({'case_id': case, 'sql_cents': sql_value,
                           'independent_csv_cents': csv_value, 'ok': True})
        # Les deux requêtes fautives proviennent des traces réelles de C08.
        faulty_values = []
        for name, (provider, model) in [('dots', PANEL5[3]), ('20b', PANEL5[4])]:
            sql = cells['C08', provider, model]['sql']
            (HERE / 'sql' / f'c08_{name}.sql').write_text(sql + '\n', encoding='utf-8')
            faulty_values.append(con.execute(sql).fetchone()[0])
        reference = next(r for r in reference_rows if r['case_id'] == 'C08')
        (HERE / 'sql/c08_reference.sql').write_text(reference['sql'] + '\n', encoding='utf-8')
        delta_sql = (HERE / 'sql/c08_delta.sql').read_text(encoding='utf-8')
        delta = [dict(row) for row in con.execute(delta_sql)]
    difference = sum(row['missed_revenue_cents'] for row in delta)
    reference_value = int(reference['revenue_cents'])
    if faulty_values != [25920, 25920] or difference != reference_value - 25920:
        raise ValueError('Le diagnostic C08 ne correspond pas aux résultats')
    save_csv('reference-check.csv', checks)
    save_csv('c08-delta.csv', delta)
    save_json('c08-results.json', {'faulty_values': faulty_values,
                                 'reference': reference_value, 'missed_cents': difference})
    # Exemple jouet de l'énoncé : borne de date incluse ou exclue.
    with sqlite3.connect(':memory:') as con:
        con.execute('CREATE TABLE sale(sale_date TEXT, amount_cents INTEGER)')
        con.execute("INSERT INTO sale VALUES ('2026-01-01', 100)")
        toy = {}
        for operator in ['>', '>=']:
            sql = f"SELECT COALESCE(SUM(amount_cents),0) FROM sale WHERE sale_date {operator} '2026-01-01' AND sale_date < '2026-01-02'"
            toy[operator] = con.execute(sql).fetchone()[0]
    save_json('demo-vote-boundary.json', {'nature': 'synthetic toy SQL', 'results': toy})
    print('20 références vérifiées ; écart C08 :', difference)


def main():
    run_script('verify-data.py', 'data-check-before.json')
    reference_rows = read_csv(HERE / 'reference-td1.csv')
    references = {r['case_id']: int(r['revenue_cents']) for r in reference_rows}
    if set(references) != {f'C{i:02}' for i in range(1, 21)}:
        raise ValueError('Il faut les 20 références')
    cells = load_cells(HERE / 'traces-td1.csv', 'real', references)
    if len(cells) != 100:
        raise ValueError('Il faut les 100 cellules du TD1')
    compare_votes(cells, references)
    check_sql(cells, reference_rows)
    run_script('atelier-vote.py', 'vote-synthetique.jsonl')
    run_script('original/atelier-routage.py', 'routage-avant.jsonl')
    run_script('atelier-routage.py', 'routage-apres.jsonl')
    router = load_module('td2_router', HERE / 'atelier-routage.py')
    resources = router.measured_resources()
    decisions = []
    for family in FAMILIES:
        for use in ['internal', 'customer', 'payout']:
            request = dict(family=family, use=use, difficulty=1, can_wait=True,
                           deadline_minutes=120, budget=0)
            decisions.append({'request': request, 'result': router.choose(request, resources)})
    save_json('routage-familles-usages.json', decisions)
    run_script('verify-data.py', 'data-check-after.json')


if __name__ == '__main__':
    main()
