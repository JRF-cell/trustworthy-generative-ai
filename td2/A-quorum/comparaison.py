"""A : comparer les quorums 2/3 et 3/5 sur les vingt questions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from td2_common import PANEL3, PANEL5, load_inputs, proposals, vote, save_json, save_csv

OUT = Path(__file__).resolve().parent / 'resultats'


def compare_votes(cells, references):
    comparison, csv_rows = [], []
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
        for (provider, model), alias in zip(PANEL5, aliases):
            cell = cells[case, provider, model]
            observations.append(f"{alias}={cell['value'] or '∅'} [{cell['verdict']}]")
        row['observations'] = '; '.join(observations)
        comparison.append(row)
        csv_rows.append({'case': case, 'reference': reference,
                         'vote_2of3': json.dumps(row['2of3']), 'vote_3of5': json.dumps(row['3of5']),
                         'observations': row['observations']})
    save_csv(OUT / 'comparison.csv', csv_rows)
    save_json(OUT / 'comparison.json', comparison)
    save_json(OUT / 'vote-summary.json', summary)
    print('Résultats des votes :', summary)


if __name__ == '__main__':
    _, references, cells = load_inputs()
    compare_votes(cells, references)
