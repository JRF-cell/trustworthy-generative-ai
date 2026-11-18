"""B : rechercher les erreurs partagées et expliquer le cas C08 en SQL."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sqlite3
from td2_common import KIT, PANEL5, PANEL3, load_inputs, proposals, vote, save_json, save_csv
from verification_csv import SPECS, independent_csv_total

HERE = Path(__file__).resolve().parent
OUT = HERE / 'resultats'


def find_shared_errors(cells, references):
    wrong = []
    for case, reference in sorted(references.items()):
        groups = {}
        for provider, model in PANEL5:
            row = cells[case, provider, model]
            if row['verdict'] == 'incorrect':
                member = {'provider': provider, 'model': model, 'sql': row['sql']}
                groups.setdefault(int(row['value']), []).append(member)
        for value, models in groups.items():
            if len(models) >= 2:
                wrong.append({'case': case, 'value': value, 'reference': reference,
                              'models': models,
                              'vote2': vote(proposals(cells, case, PANEL3), 2),
                              'vote5': vote(proposals(cells, case, PANEL5), 3)})
    save_json(OUT / 'shared-wrong-values.json', wrong)
    print('Valeurs erronées partagées :', len(wrong))


def check_sql(cells, reference_rows):
    checks = []
    db = (KIT / 'data/boutique.sqlite').as_uri() + '?mode=ro'
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
    save_csv(OUT / 'reference-check.csv', checks)
    save_csv(OUT / 'c08-delta.csv', delta)
    save_json(OUT / 'c08-results.json', {'faulty_values': faulty_values,
                                 'reference': reference_value, 'missed_cents': difference})
    # Exemple jouet de l'énoncé : borne de date incluse ou exclue.
    with sqlite3.connect(':memory:') as con:
        con.execute('CREATE TABLE sale(sale_date TEXT, amount_cents INTEGER)')
        con.execute("INSERT INTO sale VALUES ('2026-01-01', 100)")
        toy = {}
        for operator in ['>', '>=']:
            sql = f"SELECT COALESCE(SUM(amount_cents),0) FROM sale WHERE sale_date {operator} '2026-01-01' AND sale_date < '2026-01-02'"
            toy[operator] = con.execute(sql).fetchone()[0]
    save_json(OUT / 'demo-vote-boundary.json', {'nature': 'synthetic toy SQL', 'results': toy})
    print('20 références vérifiées ; écart C08 :', difference)


if __name__ == '__main__':
    reference_rows, references, cells = load_inputs()
    find_shared_errors(cells, references)
    check_sql(cells, reference_rows)
