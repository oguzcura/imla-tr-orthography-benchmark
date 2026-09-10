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

Design: 13 mechanical TDK rules (9/10 base rules + caret families verified verbatim against live TDK/GTS pages), 24-word GTS-validated caret lexicon with POS-based disambiguation, zero LLM judges, all evaluations on **price==0 free-tier endpoints** (4/21 live on 2026-09-04; $0.00 total spend).

## Paper

- `paper.tex` / `paper.pdf` — *"Copy What You See, Forget What You Know: Turkish Caret Orthography as a Surface-Form Priming Probe for Free-Tier LLMs"* (preprint build; anonymous review copy preserved on the `review-anon` branch)
- 12 pages incl. appendices: RULINGS13 adjudication table, generation log, reproducibility, transparency card (per Xu et al. 2024)

## Repository structure

```
paper.tex, paper.pdf   — manuscript (ACL preprint style, tectonic-compiled)
custom.bib             — 15 entries, every key live-verified (arXiv/Zenodo/TDK)
imla_checker3.py       — mechanical TDK-rule checker (P=1.00/R=1.00 on 22+20 validation)
prompts3.py, gen3.py   — unprimed prompt battery + free-tier generation (price==0 enforced)
score3.py              — scoring + Wilson CIs
smoke_test3.py         — checker validation suite
probe_free3.py         — free-tier endpoint prober
gts_caret_results.json — GTS-validated caret lexicon evidence
generations3.jsonl     — 657 model outputs (md5-pinned in the paper appendix)
```

## Reproduce

```bash
python probe_free3.py <model:free>...   # probe endpoints (price must be 0)
python gen3.py  google/gemma-4-31b-it:free google/gemma-4-26b-a4b-it:free minimax/minimax-m3:free
python score3.py generations3.jsonl     # per-model, per-register rates + Wilson 95% CIs
python smoke_test3.py                   # checker validation (22 positive + 20 negative)
```

Inputs are md5-pinned (manifest in paper appendix Table 6); the pipeline is idempotent and re-runnable.

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