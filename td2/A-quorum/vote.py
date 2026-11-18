"""Vote à majorité stricte, sans accès à la référence."""


def vote_k_sur_n(traces_question, k):
    n = len(traces_question)
    if type(k) is not int or not n // 2 < k <= n:
        raise ValueError("k must be an integer strict majority: n // 2 < k <= n")
    seen, groups = set(), {}
    for trace in traces_question:
        key = (trace.provider, trace.model_requested)
        if key in seen:
            raise ValueError(f"Duplicate panel member: {key}")
        seen.add(key)
        if trace.verdict == "executed" and trace.value is not None:
            if type(trace.value) is not int:
                raise ValueError("An executed value must be integer cents")
            groups.setdefault(trace.value, []).append(":".join(key))
    # Check every member before returning, including trailing duplicates.
    for value, models in groups.items():
        if len(models) >= k:
            return {"consensus": True, "value": value, "votes": len(models), "models": models}
    return {"consensus": False, "value": None,
            "votes": max((len(m) for m in groups.values()), default=0), "models": []}
