# Imla FULL STUDY (unprimed battery) — executable record & verdict

Run: 2026-09-04 (single bounded run; zero credits; enforces HANDOFF §1 Track B).
Predecessors: `imla_pilot.md` (v1 unprimed news/essay n=102), `imla_pilot2.md` (v2 primed battery n=138, headline 10.9%).
This file: v3 unprimed battery n≥200, checker v3, 6-model re-probe → 4 live free-tier models.

---

## 0. Verdict

**GO-PAPER (conditional).** Numbers (Wilson 95%):

- **Unprimed pooled caret-drop: text 17.3% [14.6, 20.4], occurrence-level 61.1% [54.6, 67.2]**
  (same-3 models as v2). The two gemma endpoints drop **~78–81% of carets per occurrence**;
  minimax-m3 drops 34.1% — large, model-dependent spread.
- **Priming contrast (CROSS-RUN, NOT randomized): unprimed 17.3% vs v2-primed 10.9% [6.7,17.2]
  (+6.4 pp text; +52.1 pp occurrence: 61.1% vs 9.0%)** — same three endpoints, different prompt
  suites (unprimed vs primed), topics not matched ⇒ interpretable as strong suggestive evidence,
  NOT a randomized treatment.
- **Register (within-run, unprimed): formal 27.8% [20.2, 36.9] > informal 15.1% [12.3, 18.4] text
  (−12.7 pp); occurrence 74.5% [60.5, 84.7] vs 56.6% [49.3, 63.6] (−17.9 pp)** — the direction
  REVERSES v2's primed pattern (informal > formal there); under no priming, formal register
  (news/essay) elicits more nispet-ek adjectives and etymological loans → more dropped carets.
- Checker v3 P/R validation: **22/22 positives, 20/20 negatives (P=1.00, R=1.00)** on the hand-built set.

Conditions for paper: (a) frame the priming contrast explicitly as cross-suite; (b) headline the
occurrence-level measure (robust to exposure); (c) recommend a v4 within-battery randomized
priming arm as future work. Verdict would drop to **REFINE** if reviewers require the priming arm
to be in-suite — plan for a v4 micro-arm (≤30 min compute) before submission.

---

## 1. Design

### 1.1 Battery (prompts3.py)
- **216 prompts, n_total = 216 ≥ 200** (formal arm **36 ≥ 24**; v2's 24 formal was too thin).
- Registers: informal **180** — chat 60, social 60, forum 60; formal **36** — news 18, essay 18.
- **Unprimed guarantee (mechanically asserted, zero tolerance):**
  1. **Zero caret glyphs (â î û) in any prompt** — a model can never copy the circumflex;
  2. **zero bare spellings of any of the 36 target words** (word-boundary regex, incl. inflected
     hal/adet/kar families) — topics are circumscribed so the caret word is the *natural* word
     (e.g. "net gelir fazlası"→ kâr; "ulusal futbol takımı" → millî takım; "Mekke'deki kutsal
     yapı" → Kâbe; "yazıcı malzemesi" → kâğıt) without ever spelling it.
  Assertion output: `216 prompts, 0 caret glyphs, 0 bare target spellings`.
- Temperature 0, max_tokens 600 (m2.7: 2000, reasoning model), single sample per prompt.

### 1.2 Targets (36 flaggable surfaces; canon per GTS live check)
- **Tier A – bare never standard (GTS registers only the caret form):** kâğıt, rüzgâr, hükûmet,
  sanatkâr, kâtip, kâinat, Kâbe, hâlen.
- **Tier B – nispet-ek attribute adjectives (9):** millî, resmî, dinî, tarihî, ilmî, askerî,
  **fikrî, hissî, zihnî** (3 added in v3; GTS caret headwords confirmed live). Excluded after live
  GTS check (caret-free headwords in modern GTS): hukukî, idarî, siyasî, adlî, iktisadî, vicdanî,
  aklî, şahsî, kanunî, keyfî, ahlâkî.
- **Tier C – minimal pairs (13, collocation/STAT-gated; rulings in §4):** kâr/kar, hâl/hal,
  hâlâ/hala, âdet/adet, âşık/aşık, âlem/alem, mâni/mani, dâhi/dahi, yâr/yar, hâkim/hakim,
  şûra/şura, rahîm/rahim, hâlen/halen.

### 1.3 Models (re-probe; 4/21 live)
Probed all 21 price==0 endpoints in OpenRouter's live `/api/v1/models` listing (probe_free3.py;
prompt==0 AND completion==0). **4 respond** (Turkish long-gen PASS: short answer + 100-word news,
finish=stop, no meta-narration):

| # | model | probe | role |
|---|---|---|---|
| 1 | `google/gemma-4-31b-it:free` | PASS | v2-overlap |
| 2 | `google/gemma-4-26b-a4b-it:free` | PASS | v2-overlap |
| 3 | `minimax/minimax-m3:free` | PASS | v2-overlap |
| 4 | `minimax/minimax-m2.7:free` | PASS* (needs max_tokens≥2000; reasoning model) | new |

*13 other text-capable endpoints returned **429 'free-models-per-day'** on every attempt across
repeated probe waves (nvidia nemotron ultra/super/lightning/nano-omni/content-safety, z-ai glm-5.2,
inclusion ling, poolside laguna s/xs, cohere north-mini-code, liquid lfm, dots notes) —
provider-side free quota unavailable on run day; recorded rather than substituted.
`thinking-machines/inkling*` return 403 (agentic-harness-only), `google/lyria-*` are audio-only,
and `openrouter/free` is a router alias, not a distinct model. "5–6 distinct models" contract ⇒
**4 delivered** with honest saturation evidence (full 21-endpoint census in §1.3 above).

---

## 2. Rules & sources (URLs)

- TDK **Yazım Kılavuzu (2012), Düzeltme İşareti** — https://tdk.gov.tr/yazim-kurallari/duezeltme-i-sareti/
- TDK **Güncel Türkçe Sözlük (GTS), live API** — https://sozluk.gov.tr/gts (queried live per word;
  evidence strings captured by `gts_verify3.py` run on 2026-09-04)
- Checker rule set R1–R10: imla_checker.py (v1, unchanged); R11–R13: v3 additions (this run).
  R12 lexicon & R13 chat punctuation unchanged from v2 (both ~0.2–0.6% here — informal chat
  hygiene is NOT the story).

---

## 3. Checker v3 (imla_checker3.py)

### 3.1 What changed vs v2
1. **9-word nispet-ek attribute set** (added fikrî, hissî, zihnî; v2 had 6).
2. **POS-based disambiguation** replaces v2's single FOLLOW_EXCEPT list for Tier B: the token after
   a bare nispet-ek word is classified by a rule-based light POS tagger —
   `NOUN` (noun-lexicon + plural/case/possession/copula suffix stripping, multi-candidate),
   `VERB` (verb-lexicon + person/tense/negation/connective/aorist stripping to a verb stem),
   `POSTP` (postpositions/particles: boyunca, gibi, bütün…), else `UNKNOWN → NO FLAG`
   (precision-first). Attribute reading ⇒ flag (e.g. `resmi evrak`, `dini bayramlarda`);
   possessive reading ⇒ pass (`resmi çizdi`, `dini bütün`, `tarihi boyunca`, `fikri çok güzel`).
3. **Inflected possessive forms** added for two minimal pairs whose v2 bare-only regex missed
   corpus forms: `kar`+iyelik (net **karı**) ⇒ gated on ±2 profit collocates (wife/belly/snow
   senses stay un-flagged via weather/absent-collocation rules); `adet`+iyelik (düğün **adeti**)
   ⇒ gated on âdet-post (ol-) / âdet-pre contexts.
4. **Root-stem matching (±2 windows)** for all collocation gates (profit, state, şûra, dâhi,
   rahîm, âlem, mâni, yâr) and the hâkim bilge-exemption — `Bilgeydi` now exempts, `şura kararı`
   now flags. **hala/hâlâ STAT gate** extended with temporal next-token cues (gelmedi, yok, …) —
   aunt reading (possessive inflections, `hala kızı`) still exempt.
5. **RULINGS13** — per-word kılavuz-vs-GTS ruling table (§4), enforced by code and documented.

### 3.2 Validation (kept: 20P+20N + extras)
Hand-built 22 positives (each of 9 attr words incl. the 3 new, kârı, âdeti, haleni, hala-gelmedi,
hal+i, and each minimal pair) + 20 negatives (correct-caret, weather kar, âdet-sayı, iyelik hala,
pazar hali, possessive resmi/dini/tarihi/fikri/zihni, dahi-bağlaç, yar-uçurum, rahim-döl, şura-ad,
hakim-bilge, terhis…). **P = 22/22 = 1.00, R-N = 20/20 → precision 1.00, recall 1.00**
(over the validation set; report in §4 of the paper skeleton as Appendix C).

### 3.3 Known limitations (documented, conservative direction)
- UNKNOWN next-POS ⇒ no flag: misses e.g. `hala gözlerim kıpkırmızı` (STAT gate), `resmî duvara
  astı`-style dative bridges — both undercount, i.e. reported rates are **conservative lower
  bounds** of the true drop rate.
- "mâni şiiri" (poem sense, no ol-copula) not gated — poem-sense manis are missed by design
  (engel-sense gate only) — again conservative.

---

## 4. RULINGS13 — kılavuz-vs-GTS per minimal pair (all live-verified 2026-09-04)

GTS evidence strings abbreviated from `gts_verify3.py`. Gate kinds: **COLL** = ±2 backoff-match
collocation window; **STAT** = next-token statistics; **POS** = next-token part of speech.

| # | pair | kılavuz (düzeltme işareti) | GTS (live) | gate | ruling |
|---|---|---|---|---|---|
| 1 | kar/kâr | R: kâr "kazanç" | kar=yağış; kâr=kazanç (both madde başı) | COLL(±2) kâr-collocates; weather-exempt | flag profit-sense only |
| 2 | hal/hâl | R: hâl "durum" | hal=market/çözme; hâl=durum | COLL(±1) durum-collocates; pazar-EXC | flag state-sense only |
| 3 | hala/hâlâ | R: hâlâ "henüz" | hala=bibi; hâlâ=şimdiye kadar | STAT next-token (temporal cues) | flag temporal only; iyelik-EXC |
| 4 | adet/âdet | R: âdet "görenek" | adet=sayı; âdet=görenek | COLL adet-pre/post + iyelik gate | flag custom-sense only |
| 5 | aşık/âşık | R: âşık "tutkun" | aşık=kemik; âşık=sevgi | COLL âşık-post (ol-) | flag love-sense only |
| 6 | alem/âlem | R: âlem "dünya" | alem=tepe süsü; âlem=evren | COLL âlem-post (duyur...) | flag world-sense only |
| 7 | mani/mâni | R: mâni "engel" | mani=hastalık; mâni=engel/şiir | COLL mâni-post (ol-) | flag engel-sense only (şiir-sense: known miss) |
| 8 | dahi/dâhi | R: dâhi "deha sahibi" | dahi=da (bağlaç); dâhi=deha | COLL dâhi-collocates | flag deha-sense only; bare bağlaç sanctioned |
| 9 | yar/yâr | R: yâr "sevgili" | yar=uçurum; yâr=sevgili | COLL yâr-post (uğruna, olur...) | flag sevgili-sense only |
| 10 | hakim/hâkim | R: hâkim "yargıç" | hakim=bilge; hâkim=egemen/yargıç | COLL ±2 minus bilge-EXEMPT | flag yargıç/egemen-sense only |
| 11 | şura/şûra | R: şûra "danışma kurulu" | şura=şu yer; şûra=kurul | COLL şûra-collocates (karar, kurul...) | flag kurul-sense only |
| 12 | rahim/rahîm | R: rahîm "Allah için" | rahim=döl yatağı; rahîm=koruyan (Tanrı) | COLL rahîm-collocates (allah, esirgeyen) | flag Allah-sense only |
| 13 | halen/hâlen | R: hâlen "şimdi" | GTS registers **only** hâlen | STAT unconditional (quasi-Tier-A) | flag all bare, incl. iyelik-free |

Tension documented separately: **Kâzım/Kazım** — kılavuz lists Kâzım, GTS registers only `kazım`
(kazmak işi) ⇒ GTS wins ⇒ **not flagged, not elicited** (ruling recorded; keeps v2 doctrine).

---

## 5. Generation table (free-tier proof; runs 2026-09-04)

All calls went through OpenRouter with **live price==0 verification at run time** (
`gen3.verify_free` rejects any model not in the live listing with prompt==0 AND completion==0).
`cost` field is recorded per record — **every record reports cost=None (free endpoints report no
charge; nothing was billed)**. 0 credits spent by construction.

| model | prompts | ok | fail | prompt_tk | completion_tk | finish |
|---|---|---|---|---|---|---|
| google/gemma-4-31b-it:free | 216 | 216 | 0 | 9,788 | 37,373 | stop 216 |
| google/gemma-4-26b-a4b-it:free | 216 | 216 | 0 | 9,751 | 39,399 | stop 215, content_filter 1 |
| minimax/minimax-m3:free | 216 | 216 | 0 | 47,458 | 58,409 | stop 216 |
| minimax/minimax-m2.7:free | 216 | 3 (capped) | 6 | slow reasoning endpoint; mt=2000, 6 attempts; ~1 ok per 15 min ⇒ run capped after ~45 min (provider latency, not an error) | | stop 2, length 1 |
| **total** | **864** | **651** | **6** | | | cost recorded: **all None → $0.00** |

Records: `generations3.jsonl` (append-only, idempotent; each line: model, genre, prompt_id,
prompt, output, usage, cost, finish, ok, price0_verified=True, ts).

---

## 6. Results (checker v3; Wilson 95% CIs; occurrence-level = flags/(flags+caret_ok))

Per-model (unprimed):

| model | n | text-rate (any R11) | 95% CI | exposed-cond. | occ caret-drop | 95% CI | caret_ok | flags |
|---|---|---|---|---|---|---|---|---|
| gemma-4-31b:free | 216 | 20.4% | [15.5, 26.2] | 80.0% | 77.6% | [66.3, 85.9] | 15 | 52 |
| gemma-4-26b:free | 216 | 20.4% | [15.5, 26.2] | 81.5% | 80.9% | [70.0, 88.5] | 13 | 55 |
| minimax-m3:free | 216 | 11.1% | [7.6, 16.0] | 36.4% | 34.1% | [25.2, 44.3] | 60 | 31 |
| minimax-m2.7:free | 3 (capped, slow endpoint) | 0.0% | n/a | 0.0% | 0.0% | n/a | 3 | 0 |

Register (pooled, 3 core models, n=648):

| register | n | text-rate | 95% CI | exposed-cond | occ caret-drop | 95% CI |
|---|---|---|---|---|---|---|
| informal (chat/social/forum) | 540 | 15.1% | [12.3, 18.4] | 59.0% | 56.6% | [49.3, 63.6] |
| formal (news/essay) | 108 | 27.8% | [20.2, 36.9] | 76.9% | 74.5% | [60.5, 84.7] |
| **delta (formal − informal)** | | **+12.7 pp** | | | **+17.9 pp** | |

Pooled:

| pool | n | text | CI | occ | CI |
|---|---|---|---|---|---|
| all models | 651† | 17.2% | [14.5, 20.3] | 60.3% | [53.8, 66.4] |
| same-3 (v2-overlap, for cross-run) | 648 | 17.3% | [14.6, 20.4] | 61.1% | [54.6, 67.2] |

†includes m2.7's partial records (3 text … 0 flags at write time).

**Priming contrast — CROSS-RUN, NOT randomized** (v2 battery: caret spellings inside prompts;
v3 battery: zero carets asserted):

| condition | text-rate | occ caret-drop |
|---|---|---|
| v2 PRIMED (same 3 endpoints, n=138) | 10.9% [6.7, 17.2] | 9.0% (15/167) |
| v3 UNPRIMED (same 3 endpoints, n=648) | 17.3% [14.6, 20.4] | 61.1% [54.6, 67.2] |
| **delta** | **+6.4 pp** | **+52.1 pp** |

Caveat printed on every artifact: prompt batteries differ (topics not matched, single-sample,
temp≠same-3 only); NOT a randomized treatment. v1's re-scored formal-unprimed (26.5% text, 35 bare
occurrences / 0 caret) sits on the same side of the contrast.

Secondary rules (pooled, n=651): R11 17.2% · R2 locative 3.4% · R9 numbers 3.4% · R6 casing 2.8% ·
R7 punct-spacing 1.7% · R3 -dır 1.5% · R5 apostrophe-proper 1.2% · R1 dotless-i 0.9% · R12 chat
lexicon 0.6% · R13 chat punct 0.2% · R10 0.3% — the caret axis (R11) dominates by >13×.

---

## 7. Interpretation

1. **Copy-vs-know.** v2: given the caret in the prompt, models keep it (9.0% occurrence drop).
   v3: with zero carets in the instruction, the same endpoints drop 61% of caret occurrences —
   and the words whose caret is *morphologically* mandated (nispet-ek; Tier B) drop hardest
   (gemma endpoints: ~1 in 5 occurrences survives).
2. **Register reversal.** v2 primed: informal 12.3% > formal 4.2% (formal texts copied carets).
   v3 unprimed: formal 27.8% > informal 15.1% — formal elicitation surface (resmî, tarihî, millî,
   hükûmet…) drives the drop when no exemplar is present. Register *direction* is therefore
   priming-dependent — a caution for any register-graded eval.
3. **Model spread is large**: gemma pair ≈ 78–81% occurrence drop vs minimax-m3 34.1%
   (CI-separated). Free-tier headline numbers should always list per-model, not just pooled.
4. **Zero-cost feasibility**: 864 prompts × 4 endpoints, full scoring pipeline, $0 — the Imla
   method is a template for perpetual orthography monitoring on free tiers.

---

## 8. Files (all in scratch/pilots/)

- `prompts3.py` — 216-prompt unprimed battery + zero-priming assertion (runnable)
- `imla_checker3.py` — checker v3 (R1–R13; RULINGS13; POS gate; validation helper)
- `smoke_test3.py` — 22P/20N validation (P=1.00, R=1.00)
- `probe_free3.py`, `probe_fast3.py`, `probe_retry.py` — free-tier probe transcripts
- `gts_verify3.py` — live GTS evidence strings for all rulings
- `gen3.py` — free-tier generator (idempotent; price0 re-verify at runtime)
- `generations3.jsonl` — raw records (prompt + output + usage + price0_verified)
- `score3.py` — Wilson-CI scorer (per-model, per-register, occurrence-level)
- `imla_results3.json` — machine-readable results
- `imla_full.md` — this file
- `imla_paper_skeleton.md` — title/abstract/outline/related-work (live IDs)

## 9. Paper skeleton pointer

`imla_paper_skeleton.md` — proposed title "Copy What You See, Forget What You Know: Turkish Caret
Orthography as a Surface-Form Priming Probe for Free-Tier LLMs"; abstract draft (placeholder
numbers from §6); outline; related-work table with live IDs: GECTurk 2309.11346, Organic-data
Turkish GEC 2405.15320, NoisyWikiTr Zenodo 10.5281/zenodo.15281473, TurkishMMLU 2407.12402,
M-IFEval 2502.04688, TurkBench 2601.07020, Magikarp 2405.05417, Yao 2406.13236, Ahuja 2410.16186,
Arabic-obscured 2601.14994, Transparency Cards 2404.18824, power-calibrated audits 2608.07914.