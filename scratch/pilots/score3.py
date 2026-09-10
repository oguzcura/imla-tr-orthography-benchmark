# -*- coding: utf-8 -*-
"""score3.py — Imla FULL STUDY scoring (checker v3 + Wilson 95% CIs).

Reads generations3.jsonl; reports:
  * R11 caret-drop: text-level (any flag), exposure-conditional, occurrence-level
  * per model, per register (informal=chat/social/forum, formal=news/essay)
  * Wilson 95% CIs everywhere
  * secondary: R12 (informal lexicon), R13 (chat punct), R1-R10 base rate
  * cross-run v2-primed comparison (10.9%) — flagged CROSS-RUN, not randomized
"""
import json, math, sys, re
sys.path.insert(0, r"C:\Users\oguzc\ai-team\research\scratch\pilots")
from imla_checker3 import check_text3, RULINGS13

OUT = r"C:\Users\oguzc\ai-team\research\scratch\pilots\generations3.jsonl"
RES = r"C:\Users\oguzc\ai-team\research\scratch\pilots\imla_results3.json"

# correct-caret occurrence regex — mirrors the flaggable bare set (incl. inflected)
CARET_OK = re.compile(
    r"kâğıt|rüzgâr|hükûmet|sanatkâr|kâtip|kâinat|Kâbe|hâlen|hâlâ|"
    r"millî|resmî|dinî|tarihî|ilmî|askerî|fikrî|hissî|zihnî|"
    r"kâr(?:ı|ım|ımız|ımızın|ımızı|ın|ını|ına|ından|ınız|ları|ların|larını|larına|"
    r"larından|larıyla|ıyla|la|dan|da)?|"
    r"hâl(?:im|in|i|ine|inden|ini|imiz|iniz|leri|leriyle|iyle|e)?|"
    r"âdet(?:im|in|i|imiz|iniz|ine|inden|leri|lerin|lerine|leriyle|iyle|e)?|"
    r"âşık|âlem|mâni|dâhi|yâr|hâkim|şûra|rahîm", re.IGNORECASE)

INFORMAL = {"chat", "social", "forum"}
FORMAL = {"news", "essay"}

# v2 primed-battery reference (imla_pilot2.md §5, checker v2, same free tier)
V2_PRIMED = {"text_rate": 15 / 138, "text_n": 138, "text_k": 15,
             "occ_rate": 15 / 167, "occ_n": 167,
             "label": "v2 PRIMED (caret spellings inside prompts)"}
V2_REG = {"informal": (14, 114), "formal": (1, 24)}


def wilson(k, n, z=1.959964):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def load():
    recs = []
    for line in open(OUT, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("ok") and r.get("output") and not r["output"].startswith("[FAIL"):
            recs.append(r)
    return recs


def score_text(text):
    v = check_text3(text)
    r11 = v.get("R11_caret", [])
    r12 = v.get("R12_informal_lexicon", [])
    r13 = v.get("R13_chat_punct", [])
    base = sum(len(x) for k, x in v.items() if k.startswith("R") and k not in
              ("R11_caret", "R12_informal_lexicon", "R13_chat_punct"))
    carets = len(CARET_OK.findall(text))
    return {"r11": len(r11), "r12": len(r12), "r13": len(r13), "base": base,
            "caret_ok": carets}


def group_stats(recs):
    n = len(recs)
    exposed = [r for r in recs if r["_s"]["r11"] > 0 or r["_s"]["caret_ok"] > 0]
    flag_texts = [r for r in recs if r["_s"]["r11"] > 0]
    flags = sum(r["_s"]["r11"] for r in recs)
    carets = sum(r["_s"]["caret_ok"] for r in recs)
    r12 = sum(1 for r in recs if r["_s"]["r12"] > 0)
    r13 = sum(1 for r in recs if r["_s"]["r13"] > 0)
    base_t = sum(1 for r in recs if r["_s"]["base"] > 0)
    return {"n": n, "exposed": len(exposed), "flag_texts": len(flag_texts),
            "text_rate": len(flag_texts) / n if n else None,
            "text_ci": wilson(len(flag_texts), n),
            "exposed_rate": len(flag_texts) / len(exposed) if exposed else None,
            "exposed_ci": wilson(len(flag_texts), len(exposed)),
            "flags": flags, "caret_ok": carets,
            "occ_rate": flags / (flags + carets) if (flags + carets) else None,
            "occ_ci": wilson(flags, flags + carets),
            "r12_rate": r12 / n if n else None, "r13_rate": r13 / n if n else None,
            "base_rate": base_t / n if n else None}


def fmt(r, key):
    if r.get(key) is None:
        return "   n/a  "
    ci = r.get(key + "_ci")
    cistr = f"[{ci[0]:.3f},{ci[1]:.3f}]" if ci else "       "
    return f"{r[key]:6.1%} {cistr}"


def main():
    recs = load()
    for r in recs:
        r["_s"] = score_text(r["output"])
    models = sorted({r["model"] for r in recs})
    out = {"meta": {"run": "imla full study, unprimed battery",
                    "checker": "imla_checker3 (RULINGS13)",
                    "n_prompts": len({(r['genre'], r['prompt_id']) for r in recs}),
                    "price0": "all models verified prompt==0 AND completion==0 at run time"},
           "models": {}, "register": {}, "pooled": {}, "v2_crossrun": {}}

    print("=" * 100)
    print("IMLA FULL STUDY — unprimed battery | checker v3 | Wilson 95%")
    print("=" * 100)
    hdr = f"{'model':<26} {'n':>4} {'text%':>8} {'CI':>17} {'expo%':>8} {'occ%':>8} {'occ CI':>17} {'caretOK':>8} {'flags':>6}"
    print(hdr)

    for m in models:
        rs = [r for r in recs if r["model"] == m]
        st = group_stats(rs)
        out["models"][m] = st
        print(f"{m[:26]:<26} {st['n']:>4} {fmt(st, 'text_rate')} {fmt(st, 'exposed_rate')} "
              f"{fmt(st, 'occ_rate')} {st['caret_ok']:>8} {st['flags']:>6}")

    # register split (pooled across models)
    print("-" * 100)
    for reg, genres in (("informal", INFORMAL), ("formal", FORMAL)):
        rs = [r for r in recs if r["genre"] in genres]
        st = group_stats(rs)
        out["register"][reg] = st
        print(f"{'REGISTER ' + reg:<26} {st['n']:>4} {fmt(st, 'text_rate')} {fmt(st, 'exposed_rate')} "
              f"{fmt(st, 'occ_rate')} {st['caret_ok']:>8} {st['flags']:>6}")
    st_i, st_f = out["register"]["informal"], out["register"]["formal"]
    if st_i["text_rate"] is not None and st_f["text_rate"] is not None:
        print(f"formal-vs-informal text-rate delta: {st_i['text_rate'] - st_f['text_rate']:+.1%} pp "
              f"(informal {st_i['text_rate']:.1%} − formal {st_f['text_rate']:.1%}); "
              f"occurrence delta {st_i['occ_rate'] - st_f['occ_rate']:+.1%} pp"
              if st_i["occ_rate"] is not None and st_f["occ_rate"] is not None else "")

    # pooled
    st = group_stats(recs)
    out["pooled"] = st
    print("-" * 100)
    print(f"{'POOLED':<26} {st['n']:>4} {fmt(st, 'text_rate')} {fmt(st, 'exposed_rate')} "
          f"{fmt(st, 'occ_rate')} {st['caret_ok']:>8} {st['flags']:>6}")

    # SAME-3 (v2-overlapping models only) for the cross-run comparison
    same3 = [r for r in recs if r["model"] in
             {"google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free",
              "minimax/minimax-m3:free"}]
    st3 = group_stats(same3)
    out["pooled_same3"] = st3
    print("-" * 100)
    print("CROSS-RUN (NOT randomized) — unprimed vs v2-primed 10.9% [6.7,17.2]:")
    print(f"  v2 primed pooled text-rate      : 15/138 = 10.9% [6.7,17.2] | occ 15/167 = 9.0%")
    print(f"  v3 unprimed pooled (all models) : {st['flag_texts']}/{st['n']} = {st['text_rate']:.1%} {st['text_ci']} | occ {st['occ_rate']:.1%} {st['occ_ci']}")
    print(f"  v3 unprimed (same 3 models)     : {st3['flag_texts']}/{st3['n']} = {st3['text_rate']:.1%} {st3['text_ci']} | occ {st3['occ_rate']:.1%} {st3['occ_ci']}")
    if st3["text_rate"] is not None:
        print(f"  priming delta (unprimed − primed, same-3, cross-run): "
              f"{st3['text_rate'] - V2_PRIMED['text_rate']:+.1%} pp text-level; "
              f"{st3['occ_rate'] - V2_PRIMED['occ_rate']:+.1%} pp occurrence-level")

    # secondary rates
    print("-" * 100)
    print(f"secondary (pooled): R12 informal-lexicon {st['r12_rate']:.1%} · "
          f"R13 chat-punct {st['r13_rate']:.1%} · R1-R10 base {st['base_rate']:.1%}")
    per_rule = {}
    for r in recs:
        v = check_text3(r["output"])
        for rid, lst in v.items():
            if lst:
                per_rule[rid] = per_rule.get(rid, 0) + 1
    n_all = len(recs)
    print("  per-rule text rates:", " · ".join(
        f"{rid} {k}/{n_all} = {100.0 * k / n_all:.1f}%" for rid, k in sorted(per_rule.items())))
    out["per_rule_text_counts"] = {k: v for k, v in sorted(per_rule.items())}

    # v2 register reference
    out["v2_crossrun"] = {"primed": V2_PRIMED,
                          "primed_register": {k: {"k": a, "n": b} for k, (a, b) in V2_REG.items()},
                          "flag": "CROSS-RUN comparison; prompt batteries differ (primed vs unprimed); not randomized — topic conflation possible"}
    out["rulings13_count"] = len(RULINGS13)
    with open(RES, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\nresults json -> {RES}")


if __name__ == "__main__":
    main()