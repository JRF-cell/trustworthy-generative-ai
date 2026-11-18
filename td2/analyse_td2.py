"""Relancer les trois parties du TD2, sans appel réseau."""
import subprocess
import sys
from td2_common import KIT, TD2, FAMILIES, load_inputs, load_module, rates, save_json


def run(script, output=None):
    result = subprocess.run([sys.executable, '-X', 'utf8', str(script)], cwd=script.parent,
                            capture_output=True, text=True, encoding='utf-8', check=True)
    if output is None:
        print(result.stdout, end='')
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.stdout, encoding='utf-8')


def main():
    run(KIT / 'verify-data.py', TD2 / 'resultats/data-check-before.json')
    run(TD2 / 'A-quorum/atelier-vote.py', TD2 / 'A-quorum/resultats/vote-synthetique.jsonl')
    run(TD2 / 'A-quorum/comparaison.py')
    run(TD2 / 'B-consensus/diagnostic_sql.py')
    run(TD2 / 'C-routing/atelier-routage-original.py', TD2 / 'C-routing/resultats/routage-avant.jsonl')
    run(TD2 / 'C-routing/atelier-routage.py', TD2 / 'C-routing/resultats/routage-apres.jsonl')
    _, _, cells = load_inputs()
    save_json(TD2 / 'C-routing/resultats/family-rates.json', rates(cells))
    router = load_module('td2_router', TD2 / 'C-routing/atelier-routage.py')
    resources = router.measured_resources()
    decisions = []
    for family in FAMILIES:
        for use in ['internal', 'customer', 'payout']:
            request = dict(family=family, use=use, difficulty=1, can_wait=True,
                           deadline_minutes=120, budget=0)
            decisions.append({'request': request, 'result': router.choose(request, resources)})
    save_json(TD2 / 'C-routing/resultats/routage-familles-usages.json', decisions)
    run(KIT / 'verify-data.py', TD2 / 'resultats/data-check-after.json')


if __name__ == '__main__':
    main()
