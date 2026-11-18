#!/usr/bin/env python3
"""TD 2: our adapted copy of td1/atelier-routage.py (subgroup 2, Pair C).

RESOURCES and choose follow our routing rule (reports/td2.md, step 3).
No API call, no key. Availability and reset times are fictitious scenarios.
The original simulator is kept unchanged in td1/atelier-routage.py.

    python3 td2/C-routing/atelier-routage.py
    python3 td2/C-routing/atelier-routage.py --scenario deferrable
"""
import argparse
import json

# TD2 rule of subgroup 2. Eligibility = 100 % correct on the family in TD1
# (model-question-comparison-en.csv). Resources are listed cheapest first
# (portfolio billed equivalent), so the first one wins a tie.
FAMILY_CELLS = {
    "F1": "C01,C04,C05,C06,C07,C20",
    "F2": "C02,C08,C09,C11",
    # F2b rests on a single TD1 cell (C10): its 1/1 rate is weak evidence.
    "F2b": "C10",
    "F3": "C03,C12,C13,C14",
    "combinations": "C15,C16,C17,C18,C19",
}

RESOURCES = [
    {"id": "gpt-oss-20b#groq-free", "access": "free", "available": True,
     "families": {"F1": "6/6", "F2b": "1/1", "F3": "4/4", "combinations": "5/5"},
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "gpt-oss-120b#groq-free", "access": "free", "available": True,
     "families": {"F1": "6/6", "F2": "4/4", "F2b": "1/1", "F3": "4/4", "combinations": "5/5"},
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "qwen3.8-27b#groq-free", "access": "free", "available": True,
     "families": {"F2": "4/4", "F3": "4/4"},
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "north-mini-code#openrouter-free", "access": "free", "available": True,
     "families": {"F1": "6/6", "F3": "4/4"},
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "dots-3-note-preview#openrouter-free", "access": "free", "available": True,
     "families": {"F1": "6/6", "F3": "4/4"},
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    # Portfolio row gpt-oss-120b#openrouter, pay-per-token 0.15 / 0.60 USD per M tokens.
    # TD1 mean for gpt-oss-120b: 641 input and 264 output tokens -> 0.00025 USD per request.
    {"id": "gpt-oss-120b#openrouter-paid", "access": "tokens", "available": True,
     "families": {"F1": "6/6", "F2": "4/4", "F2b": "1/1", "F3": "4/4", "combinations": "5/5"},
     "cash": 0.00025, "allocation": 0.00025, "reset_minutes": None},
]

# Checking per family and use (see reports/td2.md, step 3).
CHECKS = {
    "F1": {"dashboard": "none", "customer": "2-of-3 quorum", "payout": "reference SQL + human review"},
    "F2": {"dashboard": "none", "customer": "2-of-3 quorum", "payout": "reference SQL + human review"},
    "F2b": {"dashboard": "none", "customer": "reference SQL", "payout": "reference SQL + human review"},
    "F3": {"dashboard": "none", "customer": "2-of-3 quorum", "payout": "reference SQL + human review"},
    "combinations": {"dashboard": "none", "customer": "3-of-5 quorum", "payout": "reference SQL + human review"},
}


def choose(request, resources):
    """A deterministic routing policy, with a reason the user can inspect.

    Already paid capacity is preferred before new spending. A nonurgent request
    can wait for included capacity. At wake-up, availability must be measured
    again: reaching a reset time does not prove that capacity is available.
    """
    family = request["family"]
    if family not in FAMILY_CELLS:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": None,
                "reason": f"family {family} not measured in TD1, no eligible model"}
    eligible = [r for r in resources if family in r["families"]]
    checks = CHECKS[family][request["use"]]

    def td1(r):
        return f"TD1 {family} cells {FAMILY_CELLS[family]}: {r['families'][family]} correct"

    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: r["allocation"])
        return {"action": "run", "resource": chosen["id"], "cash": 0,
                "checks": checks, "reason": f"eligible included capacity, {td1(chosen)}"}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": chosen["id"], "cash": 0,
                "checks": checks, "reason": f"recheck availability at wake-up, {td1(chosen)}",
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: r["cash"])
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"],
                "checks": checks, "reason": f"available route within the authorised budget, {td1(chosen)}"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no eligible resource within deadline and budget for TD1 {family} cells {FAMILY_CELLS[family]}"}


def scenarios():
    base = {"family": "F1", "use": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}
    # Groq free quota exhausted (HTTP 429 as for qwen3.8-27b on C17-C19 in TD1).
    exhausted = [dict(r, available=False, reset_minutes=60) if r["id"].endswith("#groq-free") else dict(r)
                 for r in RESOURCES]
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "F2"}, RESOURCES),
        ("deferrable", {**base, "family": "F2"}, exhausted),
        ("urgent", {**base, "family": "F2", "can_wait": False, "deadline_minutes": 5}, exhausted),
        ("budget exhausted", {**base, "family": "F2", "can_wait": False, "budget": 0}, exhausted),
        ("high impact", {**base, "family": "F2", "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "F4"}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
