# Imla — Turkish Caret Orthography as a Surface-Form Priming Probe for Free-Tier LLMs

**Rule-verifiable evaluation of Turkish orthography fidelity in large language models — no human judges, zero API cost.**

Imla is a mechanical, TDK-grounded benchmark that measures whether LLMs respect Turkish orthography rules when generating text. The headline axis is the **caret (düzeltme işareti)**: free-tier LLMs drop required carets in **61.1% of occurrences** (Wilson 95% CI [54.6, 67.2]) under unprimed elicitation, and **copy the caret when it is primed** but do not produce it autonomously (occurrence-level priming contrast significant at every threshold: Fisher p = 6.2×10⁻²⁸).

## Key results (all statistical claims multiplicity-corrected; see paper §4.6)

| Contrast | Finding | Standing |
|---|---|---|
| Occurrence-level caret drop (unprimed, N=648, 3 models) | **61.1%** [54.6, 67.2] | robust (Fisher p = 9.2×10⁻¹² model spread) |
| Text-level violation rate | **17.3%** [14.6, 20.4] | robust for model spread |
| Priming (unprimed vs primed, occurrence-level) | 61.1% vs 9.0% | **robust** (p = 6.2×10⁻²⁸) |
| Priming (text-level) | 17.3% vs 10.9% | **n.s.** (p = 0.074) — reported as exploratory |
| Register (unprimed, text-level) | formal 27.8% vs informal 15.1% | suggestive (Holm-only) |

Design: 13 mechanical TDK rules (9/10 base rules + caret families verified verbatim against live TDK/GTS pages), 36 flaggable caret surface forms (30 GTS-validated headwords) with POS-based disambiguation, zero LLM judges, all evaluations on **price==0 free-tier endpoints** (4/21 live on 2026-09-04; $0.00 total spend).

## Paper

- `paper.tex` / `paper.pdf` — *"Copy What You See, Forget What You Know: Turkish Caret Orthography as a Surface-Form Priming Probe for Free-Tier LLMs"* (preprint build; anonymous review copy preserved on the `review-anon` branch)
- 13 pages incl. appendices: RULINGS13 adjudication table, generation log, reproducibility, transparency card (per Xu et al. 2024)

## Repository structure

The executable record of the run lives under `scratch/pilots/` (paths relative to the repo root, matching the paper's §7 manifest). The 11 files pinned in the paper's md5 table (Table 7) are byte-identical; the remaining two support artifacts (`imla_checker2.py`, `gts_caret_results.json`) complete the §7 manifest:

```
paper.tex, paper.pdf          — manuscript (ACL preprint style, tectonic-compiled)
custom.bib                    — 15 entries, every key live-verified (arXiv/Zenodo/TDK)
scratch/pilots/
  imla_checker3.py            — mechanical TDK-rule checker v3 (P=1.00/R=1.00 on 22+20 validation)
  prompts3.py                 — 216-prompt unprimed battery + zero-priming assertion
  gen3.py                     — free-tier generation harness (idempotent; re-verifies price==0)
  score3.py                   — scoring + Wilson 95% CIs
  smoke_test3.py              — checker validation suite (22 positive + 20 negative)
  probe_free3.py              — free-tier endpoint prober (reads OPENROUTER_API_KEY from env)
  gts_verify3.py              — live GTS headword evidence for all rulings
  gts_caret_results.json      — GTS-validated caret lexicon evidence
  generations3.jsonl          — 657 model outputs (md5-pinned in the paper appendix)
  imla_results3.json          — machine-readable results (verbatim source of all tables)
  rigor_stats_compute.py      — recomputes every inferential number (needs scipy)
  imla_full.md                — run manifest & verdict
```

## Reproduce

From the repo root (scripts resolve their sibling modules relative to `scratch/pilots/`):

```bash
python scratch/pilots/probe_free3.py <model:free>...   # probe endpoints (price must be 0; needs OPENROUTER_API_KEY)
python scratch/pilots/gen3.py  google/gemma-4-31b-it:free google/gemma-4-26b-a4b-it:free minimax/minimax-m3:free
python scratch/pilots/score3.py                        # per-model, per-register rates + Wilson 95% CIs
python scratch/pilots/smoke_test3.py                   # checker validation (22 positive + 20 negative)
```

`gen3.py` appends new runs to `scratch/pilots/generations3.jsonl`; scoring the released file reproduces the paper's numbers. Inputs are md5-pinned (manifest in paper appendix Table 7); the pipeline is idempotent and re-runnable.

## License

- **Code** (checker, prompts, scoring, probing scripts): [MIT](LICENSE-CODE)
- **Paper text, tables, and results**: [CC BY 4.0](LICENSE)

## Citation

```bibtex
@misc{cura2026imla,
  author = {Cura, O\u{g}uz Emre},
  title  = {Copy What You See, Forget What You Know: Turkish Caret Orthography as a Surface-Form Priming Probe for Free-Tier LLMs},
  year   = {2026},
  note   = {Independent Research},
  howpublished = {\url{https://github.com/oguzcura/imla-tr-orthography-benchmark}}
}
```

## Contact

Oğuz Emre Cura · oguzemrecura@gmail.com · [github.com/oguzcura](https://github.com/oguzcura) · Independent Researcher

---

*Research conducted with disclosed AI-assisted workflows; every number in this repository re-derivable from the pinned artifacts.*