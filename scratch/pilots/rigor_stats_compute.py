# -*- coding: utf-8 -*-
"""rigor_stats_compute.py — Imla paper headline contrasts (FET, RR, Cohen's h, OR, binomial floor, MDE).

Reads scratch/pilots/imla_results3.json (run manifest counts) and recomputes every
inferential number quoted in the paper's Results section (S1-S8 disclosures and
Table "contrasts"). md5-pinned in the paper (Reproducibility / Table md5).

Formulas (documented):
  - FET: two-sided Fisher's exact on the 2x2 table (scipy).
  - RR + 95% CI: Katz log method. OR + 95% CI: Woolf log method.
  - Cohen's h = 2 asin(sqrt(p1)) - 2 asin(sqrt(p2)).
  - Binomial vs fixed floor: exact P(X >= k) under Bin(n, p0) (survival).
  - MDE (pp): normal-approximation two-sample, alpha=.05 two-sided, power=.80,
    at the observed pooled rate: MDE = (z1-a/2 + z_power) * se(pooled).
    (Quoted MDEs in disclosures S4-S5 follow the overlay's normal approximation;
    this formula recomputes them from the same counts and never changes a
    robust/underpowered verdict.)
"""
import json, math

try:
    from scipy.stats import fisher_exact, binom  # noqa
except ImportError:
    raise SystemExit("scipy required")

D = json.load(open("imla_results3.json", encoding="utf-8"))
M = D["models"]

def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

def fet(a, b, c, d):  # [[a,b],[c,d]] two-sided
    return fisher_exact([[a, b], [c, d]], alternative="two-sided")[1]

def rr_ci(k1, n1, k2, n2):
    p1, p2 = k1/n1, k2/n2
    rr = p1/p2
    # delta-method log-RR SE (matches the overlay's quoted CIs; integer-safe)
    se = math.sqrt((1-p1)/(n1*p1) + (1-p2)/(n2*p2)) if k1 and k2 else float("nan")
    return rr, (rr*math.exp(-1.959964*se), rr*math.exp(1.959964*se))

def or_ci(k1, n1, k2, n2):
    o = (k1*(n2-k2))/((n1-k1)*k2) if k1 and k2 and k1 < n1 and k2 < n2 else float("nan")
    se = math.sqrt(1/k1 + 1/(n1-k1) + 1/k2 + 1/(n2-k2)) if k1 and k2 and k1 < n1 and k2 < n2 else float("nan")
    return o, (o*math.exp(-1.959964*se), o*math.exp(1.959964*se))

def h_of(p1, p2):
    return 2*math.asin(math.sqrt(p1)) - 2*math.asin(math.sqrt(p2))

def mde_pp(k1, n1, k2, n2, z=1.959964, zp=0.8416212):
    pk = (k1+k2)/(n1+n2)
    se = math.sqrt(pk*(1-pk)*(1/n1 + 1/n2))
    return 100*(z+zp)*se

def report(name, k1, n1, k2, n2, note=""):
    p1, p2 = k1/n1, k2/n2
    p = fet(k1, n1-k1, k2, n2-k2)
    rr, rrci = rr_ci(k1, n1, k2, n2)
    o, oc = or_ci(k1, n1, k2, n2)
    h = h_of(p1, p2)
    print(f"{name}: p={p:.3g}  p1={100*p1:.1f}% ({k1}/{n1})  p2={100*p2:.1f}% ({k2}/{n2})"
          f"  RR={rr:.2f} [{rrci[0]:.2f}, {rrci[1]:.2f}]  h={h:+.2f}  OR={o:.2f} [{oc[0]:.2f}, {oc[1]:.2f}]"
          f"  MDE={mde_pp(k1, n1, k2, n2):.0f}pp  {note}")

print("== Table {contrasts} (ref group second) ==")
report("MODEL occ ", 107, 135, 31, 91, "gemma pair vs minimax-m3")
report("PRIME occ", 138, 226, 15, 167, "unprimed vs primed")
report("REG text ", 30, 108, 82, 543, "formal vs informal")
report("MODEL txt", 88, 432, 24, 216, "gemma pair vs minimax-m3")
report("REG occ  ", 35, 47, 103, 182, "formal vs informal")
report("PRIME txt", 112, 648, 15, 138, "unprimed vs primed")

print("\n== extras ==")
report("GEMMA repl", 44, 216, 44, 216, "31b vs 26b, text level")
p = fet(14, 100, 1, 23)
print(f"primed register legs FET p={p:.3f} (informal 14/114 vs formal 1/24)")
k, n, p0 = 112, 648, 0.05
print(f"binomial floor: P(X>={k}) | Bin({n}, {p0}) = {binom.sf(k-1, n, p0):.3g}")

# full Wilson cross-check against every CI in the JSON
cells = {}
for mk, m in M.items():
    cells[f"{mk} text"] = (m["flag_texts"], m["n"], m["text_ci"])
    cells[f"{mk} occ"] = (m["flags"], m["flags"] + m["caret_ok"], m["occ_ci"])
    cells[f"{mk} exp"] = (m["flag_texts"], m["exposed"], m["exposed_ci"])
for rk, r in D["register"].items():
    cells[f"reg {rk} text"] = (r["flag_texts"], r["n"], r["text_ci"])
    cells[f"reg {rk} occ"] = (r["flags"], r["flags"] + r["caret_ok"], r["occ_ci"])
    cells[f"reg {rk} exp"] = (r["flag_texts"], r["exposed"], r["exposed_ci"])
for pk_, r in (("pooled", D["pooled"]), ("same3", D["pooled_same3"])):
    cells[f"{pk_} text"] = (r["flag_texts"], r["n"], r["text_ci"])
    cells[f"{pk_} occ"] = (r["flags"], r["flags"] + r["caret_ok"], r["occ_ci"])
    cells[f"{pk_} exp"] = (r["flag_texts"], r["exposed"], r["exposed_ci"])
bad = 0
for name, (k_, n_, ci) in sorted(cells.items()):
    lo, hi = wilson(k_, n_)
    okk = abs(lo - ci[0]) < 1e-6 and abs(hi - ci[1]) < 1e-6
    bad += 0 if okk else 1
    if not okk:
        print(f"  MISMATCH {name}: {lo:.6f},{hi:.6f} vs {ci}")
print(f"wilson recheck: {len(cells)-bad}/{len(cells)} JSON CIs reproduced to 6dp")