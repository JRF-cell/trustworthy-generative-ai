"""Local deterministic references, checked independently on the distributed CSVs.

These are new local calculations, not the group's historical TD1 work.
No model call. Python standard library only.
"""
import csv
import re
import sqlite3
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Explicit transcription of the twenty questions: period, reference date,
# age at order, allowed products. Bounds are [start, end).
SPECS = {
    'C01': ('2026-03-01', '2026-06-01', None, False, None),
    'C02': (None, None, '2026-09-25', False, None),
    'C03': ('2026-01-01', '2026-07-01', None, False, 'abc'),
    'C04': ('2026-01-01', '2026-10-01', None, False, None),
    'C05': ('2026-06-01', '2026-06-02', None, False, None),
    'C06': ('2025-01-01', '2026-01-01', None, False, None),
    'C07': ('2026-05-31', '2026-06-01', None, False, None),
    'C08': (None, None, '2026-09-24', False, None),
    'C09': (None, None, '2026-09-26', False, None),
    'C10': (None, None, None, True, None),
    'C11': (None, None, '2026-12-01', False, None),
    'C12': (None, None, None, False, 'abc'),
    'C13': ('2026-04-01', '2026-05-01', None, False, 'ac'),
    'C14': ('2026-10-01', '2026-12-01', None, False, 'abc'),
    'C15': ('2026-03-01', '2026-06-01', '2026-09-25', False, None),
    'C16': (None, None, '2026-09-25', False, 'abc'),
    'C17': ('2026-01-01', '2026-07-01', '2026-09-25', False, 'abc'),
    'C18': ('2026-05-01', '2026-06-01', None, True, None),
    'C19': ('2026-09-01', '2026-10-01', '2026-09-25', False, 'd'),
    'C20': ('2026-06-01', '2026-09-01', None, False, None),
}


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def query(spec):
    start, end, reference, at_order, products = spec
    conditions = []
    if start:
        conditions += [f"o.date >= '{start} 00:00:00'", f"o.date < '{end} 00:00:00'"]
    if reference or at_order:
        target = 'date(o.date)' if at_order else f"'{reference}'"
        conditions += [f"c.birth_date > date({target}, '-26 years')",
                       f"c.birth_date <= date({target}, '-25 years')"]
    if products:
        conditions.append('p.product_id IN (' + ', '.join(repr(p) for p in products) + ')')
    return ('SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents\n'
            'FROM orders o JOIN product p ON p.product_id = o.product_id\n'
            'JOIN customers c ON c.customer_id = o.customer_id\nWHERE '
            + ' AND '.join(conditions or ['1=1']) + ';')


def independent_csv_total(spec):
    start, end, reference, at_order, products = spec
    customers = {c['customer_id']: date.fromisoformat(c['birth_date'])
                 for c in read_csv(HERE / 'data/customers.csv')}
    prices = {p['product_id']: int(p['price']) for p in read_csv(HERE / 'data/product.csv')}
    total = 0
    for order in read_csv(HERE / 'data/orders.csv'):
        when = order['date']
        if start and not start + ' 00:00:00' <= when < end + ' 00:00:00':
            continue
        if products and order['product_id'] not in products:
            continue
        if reference or at_order:
            target = date.fromisoformat(when[:10] if at_order else reference)
            birth = customers[order['customer_id']]
            age = target.year - birth.year - ((target.month, target.day) < (birth.month, birth.day))
            if age != 25:
                continue
        total += int(order['quantity_product']) * prices[order['product_id']]
    return total


def main():
    official = {}
    for line in (HERE / 'reference-values-officielles.md').read_text(encoding='utf-8').splitlines():
        if re.match(r'\| C\d\d \|', line):
            parts = line.split('|')
            official[parts[1].strip()] = int(parts[3].strip())
    rows, checks = [], []
    with sqlite3.connect((HERE / 'data/boutique.sqlite').as_uri() + '?mode=ro', uri=True) as con:
        for case, spec in SPECS.items():
            sql = query(spec)
            value = con.execute(sql).fetchone()[0]
            independent = independent_csv_total(spec)
            if not value == independent == official[case]:
                raise ValueError(f'{case}: SQL={value}, CSV={independent}, officiel={official[case]}')
            rows.append({'case_id': case, 'sql': sql, 'revenue_cents': value})
            checks.append({'case_id': case, 'sql_cents': value, 'csv_cents': independent,
                           'official_cents': official[case], 'ok': True})
    for name, data in [('reference-locale.csv', rows), ('evidence/reference-check.csv', checks)]:
        with (HERE / name).open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    print('20 references verified: SQL = independent CSV computation = official values.')


if __name__ == '__main__':
    main()
