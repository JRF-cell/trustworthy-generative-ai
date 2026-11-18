"""Choisir un modèle à partir des résultats TD1. Simulation sans appel réseau."""
import argparse
import json
from td2_common import HERE, PANEL5, FAMILIES, load_cells, rates, read_csv

# The five TD1 access routes are free under the supplied course protocol.
# Availability is simulated; no provider request is made.
RESOURCES = [dict(id=f'{p}:{m}', provider=p, model=m, access='free',
                  available=True, cash=0.0, allocation=0.0, reset_minutes=None,
                  evidence={}) for p, m in PANEL5]


def measured_resources():
    refs = {r['case_id']: int(r['revenue_cents']) for r in read_csv(HERE / 'reference-td1.csv')}
    stats = rates(load_cells(HERE / 'traces-td1.csv', 'real', refs))
    resources = []
    for resource in RESOURCES:
        evidence = {}
        for stat in stats:
            if (stat['provider'], stat['model']) == (resource['provider'], resource['model']):
                evidence[stat['family']] = stat
        resources.append(dict(resource, evidence=evidence))
    return resources


def choose(request, resources):
    family = request['family']
    cases = ', '.join(FAMILIES.get(family, [])) or 'unknown family'
    use = request.get('use', 'internal')
    if use not in {'internal', 'customer', 'payout'}:
        raise ValueError('Unknown use')
    eligible, summary = [], []
    for r in resources:
        evidence = r.get('evidence', {}).get(family, {})
        complete = evidence.get('complete', False)
        total, correct = evidence.get('total', 0), evidence.get('correct', 0)
        perfect = complete and total > 0 and correct == total
        level = 0
        if complete and correct > 0:
            level = 1
        if perfect:
            level = 3
        ratio = f'{correct}/{total}' if complete else 'ND'
        summary.append(f"{r['id']}={ratio}")
        if level and level >= request.get('difficulty', 1):
            eligible.append(dict(r, level=level, perfect=perfect, ratio=ratio))

    def rank(r):
        # At equal cost, favour full observed accuracy, then stable model ID.
        return r['cash'], r['allocation'], not r['perfect'], r['id']

    def decision(action, chosen=None, explanation='', wake_in_minutes=None):
        detail = f"{chosen['id']}={chosen['ratio']}" if chosen else '; '.join(summary)
        checks = 'reference + human review' if use == 'payout' else 'reference'
        if chosen and use == 'internal' and chosen['perfect'] and chosen['cash'] == 0:
            checks = 'none'
        result = dict(action=action, resource=chosen['id'] if chosen else None,
                      cash=chosen['cash'] if chosen and action == 'run' else 0,
                      checks=checks, reason=f'{family} [{cases}]; {detail}; {explanation}')
        if wake_in_minutes is not None:
            result['wake_in_minutes'] = wake_in_minutes
        return result

    included = [r for r in eligible if r['available'] and r['cash'] == 0]
    waiting = [r for r in eligible if not r['available'] and r['cash'] == 0
               and r['reset_minutes'] is not None
               and 0 < r['reset_minutes'] <= request['deadline_minutes']]
    if included:
        return decision('run', min(included, key=rank), 'eligible included capacity')
    if request['can_wait'] and waiting:
        chosen = min(waiting, key=lambda r: (r['reset_minutes'], rank(r)))
        return decision('defer', chosen, 'recheck availability at wake-up',
                        wake_in_minutes=chosen['reset_minutes'])
    paid = [r for r in eligible if r['available'] and r['cash'] <= request['budget']]
    if paid:
        return decision('run', min(paid, key=rank), 'available route within budget')
    return decision('abstain', explanation='no measured eligible route within deadline and budget')


def scenarios(resources):
    base = dict(family='F1', difficulty=1, use='internal', can_wait=True,
                deadline_minutes=120, budget=0.30)
    exhausted = [dict(r, available=False, reset_minutes=60) for r in resources]
    return [
        ('simple', base, resources),
        ('complex', dict(base, family='F1+F2+F3', difficulty=3), resources),
        ('deferrable', base, exhausted),
        ('urgent', dict(base, can_wait=False, deadline_minutes=5), exhausted),
        ('budget exhausted', dict(base, can_wait=False, budget=0), exhausted),
        ('high impact', dict(base, family='F2', difficulty=3, use='payout'), resources),
        ('unknown capability', dict(base, difficulty=4), resources),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario')
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios(measured_resources()):
        if args.scenario and args.scenario != name:
            continue
        found = True
        print(json.dumps(dict(scenario=name, nature='simulation', request=request,
                              result=choose(request, resources))))
    if not found:
        parser.error('Unknown scenario')


if __name__ == '__main__':
    main()
