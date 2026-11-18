"""Vérification indépendante : calcul des 20 réponses sur les CSV en Python."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import date
from td2_common import KIT, read_csv

# Pour chaque question : début, fin, date de référence, âge à la commande, produits.
# Les périodes sont de la forme [début, fin[.
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

def independent_csv_total(spec):
    start, end, reference, at_order, products = spec
    customers = {c['customer_id']: date.fromisoformat(c['birth_date'])
                 for c in read_csv(KIT / 'data/customers.csv')}
    prices = {p['product_id']: int(p['price']) for p in read_csv(KIT / 'data/product.csv')}
    total = 0
    for order in read_csv(KIT / 'data/orders.csv'):
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
