"""TD2 step 1: fixed 2-of-3 panel versus 3-of-5 quorum on the TD1 traces.
Run from the repository root: python3 td2/vote_td2.py
Reads the TD1 files in kit-td1/, writes td2/vote-comparison-td2.csv. No network call.
"""
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

TD2 = Path(__file__).resolve().parent
KIT = TD2.parent / "kit-td1"

PANEL_3 = [
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
]
PANEL_5 = [
    ("groq", "openai/gpt-oss-120b"),
    ("groq", "openai/gpt-oss-20b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
    ("openrouter", "dots-studio/dots-3-note-preview:free"),
]

spec = importlib.util.spec_from_file_location("skeleton", KIT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules["skeleton"] = skeleton
spec.loader.exec_module(skeleton)


def vote(proposals, k):
    return skeleton.Orchestrateur.vote_k_sur_n(None, proposals, k)


with open(KIT / "traces-td1.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
with open(KIT / "reference-td1.csv", encoding="utf-8", newline="") as f:
    references = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(f)}


def proposals(case, panel):
    # Same rule as atelier-vote.py: the last attempt of each member,
    # an error or a missing value stays in n without a vote.
    last = {}
    for r in rows:
        if r["case_id"] == case and r["nature"] == "real":
            last[(r["provider"], r["model_requested"])] = r
    result = []
    for provider, model in panel:
        r = last.get((provider, model), {})
        ok = r.get("verdict") in ("correct", "incorrect") and r.get("value", "") != ""
        result.append(SimpleNamespace(provider=provider, model_requested=model,
                                      value=int(r["value"]) if ok else None,
                                      verdict="executed" if ok else "error"))
    return result


def text(decision):
    if decision["consensus"]:
        return f"consensus {decision['value']} ({decision['votes']} votes)"
    return f"abstention (max {decision['votes']} votes)"


columns = ["case_id", "reference_cents", "values_5_models",
           "vote_2of3", "match_2of3", "vote_3of5", "match_3of5", "decision_changes"]
table = []
for case in sorted(references):
    ref = references[case]
    five = proposals(case, PANEL_5)
    d23 = vote(proposals(case, PANEL_3), 2)
    d35 = vote(five, 3)
    table.append({
        "case_id": case,
        "reference_cents": ref,
        "values_5_models": " | ".join(f"{p.model_requested}={p.value if p.value is not None else 'error'}" for p in five),
        "vote_2of3": text(d23),
        "match_2of3": (d23["value"] == ref) if d23["consensus"] else "",
        "vote_3of5": text(d35),
        "match_3of5": (d35["value"] == ref) if d35["consensus"] else "",
        "decision_changes": (d23["consensus"], d23["value"]) != (d35["consensus"], d35["value"]),
    })

with open(TD2 / "vote-comparison-td2.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(table)

for t in table:
    print(t["case_id"], t["reference_cents"], "|", t["vote_2of3"], t["match_2of3"],
          "|", t["vote_3of5"], t["match_3of5"], "| changes:", t["decision_changes"])
