"""Lecture des traces et fonctions communes au vote et au routage."""
import csv
import json
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

TD2 = Path(__file__).resolve().parent
KIT = TD2.parent / 'kit-td1'
PANEL3 = [('groq', 'openai/gpt-oss-120b'),
          ('openrouter', 'cohere/north-mini-code:free'), ('groq', 'qwen/qwen3.8-27b')]
PANEL5 = PANEL3 + [('openrouter', 'dots-studio/dots-3-note-preview:free'),
                   ('groq', 'openai/gpt-oss-20b')]
# Disjoint groups reflect the actual predicates, including combinations.
FAMILIES = {
    'F1': ['C01', 'C04', 'C05', 'C06', 'C07', 'C20'],
    'F2': ['C02', 'C08', 'C09', 'C11'], 'F2b': ['C10'], 'F3': ['C12'],
    'F1+F3': ['C03', 'C13', 'C14'], 'F1+F2': ['C15'],
    'F2+F3': ['C16'], 'F1+F2+F3': ['C17', 'C19'], 'F1+F2b': ['C18'],
}


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def vote(proposals, k):
    if 'td2_vote' not in sys.modules:
        load_module('td2_vote', TD2 / 'A-quorum/vote.py')
    return sys.modules['td2_vote'].vote_k_sur_n(proposals, k)


def load_cells(path, nature, references):
    if not Path(path).exists():
        return {}
    rows = read_csv(path)
    required = {'provider', 'model_requested', 'case_id', 'nature', 'value', 'verdict'}
    if rows and not required <= rows[0].keys():
        raise ValueError(f'Missing trace columns: {required - rows[0].keys()}')
    cells = {}
    for row in rows:
        key = row['provider'], row['model_requested']
        case = row['case_id']
        if row['nature'] != nature or key not in PANEL5 or case not in references:
            continue
        if row.get('reference') and int(row['reference']) != references[case]:
            raise ValueError(f'Conflicting reference for {case}: check experiment identity')
        if row['verdict'] in {'correct', 'incorrect'}:
            if row['value'] == '':
                raise ValueError(f'Missing executed value: {case}, {key}')
            correct = int(row['value']) == references[case]
            if correct != (row['verdict'] == 'correct'):
                raise ValueError(f'Inconsistent value/verdict for {case}, {key}')
        cells[case, *key] = row  # chronological export: final row = last attempt
    return cells


def proposals(cells, case, panel):
    result = []
    for provider, model in panel:
        row = cells.get((case, provider, model), {})
        executed = row.get('verdict') in {'correct', 'incorrect'} and row.get('value') not in ('', None)
        result.append(SimpleNamespace(provider=provider, model_requested=model,
                                     value=int(row['value']) if executed else None,
                                     verdict='executed' if executed else 'error'))
    return result


def rates(cells):
    output = []
    for family, cases in FAMILIES.items():
        for provider, model in PANEL5:
            correct = 0
            observed = 0
            details = []
            for case in cases:
                row = cells.get((case, provider, model), {})
                if row:
                    observed += 1
                if row.get('verdict') == 'correct':
                    correct += 1
                details.append({'case': case, 'verdict': row.get('verdict', 'missing'),
                                'value': row.get('value', '')})
            output.append({'family': family, 'provider': provider, 'model': model,
                           'cases': cases, 'correct': correct, 'total': len(cases),
                           'observed': observed, 'complete': observed == len(cases),
                           'cells': details})
    return output


def load_inputs():
    reference_rows = read_csv(KIT / 'reference-td1.csv')
    references = {row['case_id']: int(row['revenue_cents']) for row in reference_rows}
    if set(references) != {f'C{i:02}' for i in range(1, 21)}:
        raise ValueError('Il faut les 20 références')
    cells = load_cells(KIT / 'traces-td1.csv', 'real', references)
    if len(cells) != 100:
        raise ValueError('Il faut les 100 cellules du TD1')
    return reference_rows, references, cells


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def save_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
