# Imla Paper — Turkish Orthography Fidelity of Free-Tier LLM Endpoints

Standalone paper draft (TMLR/workshop-ready: main text + appendix) reporting an
orthographic audit of free-tier LLM endpoints for Turkish **düzeltme işareti**
("imla") caret dropping. Part of the Track-B pilot series; sibling projects:
`../ecosystem-audit/`, `../trmlu-audit/`.

## Status

- Draft: **v1 2026-09-04** (anonymous `[review]` mode; flip to `preprint` for
  named submission — author line: real name, "Independent Researcher",
  oguzemrecura@gmail.com, github oguzcura).
- Compiles clean under **tectonic**; zero overfull boxes, zero undefined
  citations, Turkish glyphs verified in the PDF text layer.
- Every number in the paper is transcribed verbatim from
  `../scratch/pilots/imla_results3.json` (the machine-readable run record).
- No numbers are re-derived inside the paper; all statistics are reproduced by
  the pinned `rigor_stats_compute.py` (md5 published in the appendix).

## Content map

- `paper.tex` — main draft (introduction / related work / method / results /
  discussion / limitations / reproducibility appendix / 13-rule adjudication
  table / generation log / transparency card).
- `custom.bib` — 15 references, **every entry live-verified 2026-09-04**
  (arXiv Atom API, Zenodo, TDK); no fabricated metadata.
- `acl.sty` + `acl_natbib.bst` — ACL 2023 style files (copied from
  `../trmlu-audit/paper/`), used for the TMLR/workshop format.
- `lineno.sty` — vendored CTAN copy (distro copy carries an invalid UTF-8 byte
  that breaks tectonic's license report).
- `out/paper.pdf` — latest build.

## Build

```sh
export PATH=$HOME/bin:$PATH   # tectonic static binary
cd research/imla-paper
rm -rf out && mkdir -p out
tectonic --keep-intermediates -o out paper.tex
```

Verify: `python3 _verify_pdf.py` (glyph/integrity checks), `python3 _scan_log.py`
(overfull sweep), `python3 _ascii_check.py` (source stays 7-bit ASCII; Turkish
diacritics are written as LaTeX commands, e.g. `\u{g}` for ğ).

## Key results (all verbatim from imla_results3.json)

- 864 prompts; 651 completed records (6 failed; reasoning endpoint capped at 3);
  $0.00 total spend (free-tier endpoints, live price verification).
- Text-level caret-drop rate: **17.3%** [14.6, 20.4]; occurrence-level: **61.1%**
  [54.6, 67.2] (same-3 pool, n=648).
- Per-model text rates 20.4%–20.4% (both Gemma endpoints) vs minimax-m3;
  occurrence rates 77.6%–80.9% vs **34.1%**.
- Register: formal news/essay **27.8%** vs informal **15.1%** (RR=1.84
  [1.28, 2.65]).
- Priming comparison (v2 PRIMED vs v3 UNPRIMED): **cross-run caveat flagged in
  the paper**; occurrence-level contrast 9.0% vs 61.1% is the cleanest reading;
  the text-level contrast is underpowered (n.s.).

## Provenance

Run record / source of truth: `../scratch/pilots/imla_full.md`. Executables:
`prompts3.py`, `gen3.py`, `imla_checker3.py`, `smoke_test3.py`,
`gts_verify3.py`, `score3.py`, `rigor_stats_compute.py` — md5 pins in the
paper's reproducibility appendix. Pre-registration: `../ecosystem-audit/
pre_registration_2026-09-04.md` (retrospective registration disclosed in the
paper, per the rigor overlay).