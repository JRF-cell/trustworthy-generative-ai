"""Shared offline analysis, keeping missing observations distinct from errors."""
import importlib.util
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from build_references import read_csv

HERE = Path(__file__).resolve().parent
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


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def vote(proposals, k):
    if 'td2_skeleton' not in sys.modules:
        load_module('td2_skeleton', HERE / 'skeleton-multi-llm-en.py')
    return sys.modules['td2_skeleton'].Orchestrateur.vote_k_sur_n(None, proposals, k)


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
            rows = [cells.get((case, provider, model)) for case in cases]
            counts = Counter(r['verdict'] for r in rows if r)
            output.append({'family': family, 'provider': provider, 'model': model,
                           'cases': cases, 'correct': counts['correct'], 'total': len(cases),
                           'observed': sum(r is not None for r in rows),
                           'complete': all(r is not None for r in rows),
                           'cells': [{ 'case': case, 'verdict': row.get('verdict', 'missing'),
                                       'value': row.get('value', '') }
                                     for case, row in zip(cases, [r or {} for r in rows])]})
    return output
