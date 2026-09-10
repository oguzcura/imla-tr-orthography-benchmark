# -*- coding: utf-8 -*-
"""gen3.py — Imla FULL STUDY generation, FREE-TIER ONLY.

* Models must appear in the LIVE OpenRouter /api/v1/models listing with
  prompt==0 AND completion==0 at run time (re-probed: see probe_free3.py).
* Unprimed prompt battery from prompts3.py (asserted 0 caret glyphs /
  0 bare target spellings).
* Idempotent append to generations3.jsonl (skips existing model+genre+pid).
* Retries with backoff; every record carries usage + price0_verified.
"""
import json, os, sys, time, threading
sys.path.insert(0, r"C:\Users\oguzc\ai-team\research\scratch\pilots")
from probe_free3 import live_free_models, call
from prompts3 import PROMPTS, assert_unprimed

OUT = r"C:\Users\oguzc\ai-team\research\scratch\pilots\generations3.jsonl"
DEFAULT_MODELS = [  # locked by live re-probe (2026-09-04): 4/21 price==0 endpoints respond;
    # 13 others: 429 'free-models-per-day' (provider-side quota); inkling* 403 agentic-only;
    # lyria* audio-only; openrouter/free alias. Documented in imla_full.md §models.
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "minimax/minimax-m3:free",
    "minimax/minimax-m2.7:free",
]
MAX_TOKENS = {"minimax/minimax-m2.7:free": 2000}  # reasoning model: needs budget for reasoning+answer
MAX_ATTEMPTS = {"minimax/minimax-m2.7:free": 6}
MAX_WORKERS = 6
_stats = {"ok": 0, "fail": 0, "skip": 0}
_stats_lock = threading.Lock()


def verify_free(models):
    ids = {f["id"] for f in live_free_models()}
    missing = [m for m in models if m not in ids]
    if missing:
        raise SystemExit(f"BLOCKED-FREE-TIER: not price==0 in live listing: {missing}")
    print(f"[verify] {len(models)} models confirmed price==0 live: {models}")


def load_done():
    done = set()
    if not os.path.exists(OUT):
        return done
    for line in open(OUT, encoding="utf-8"):
        try:
            r = json.loads(line)
            if r.get("ok"):
                done.add((r["model"], r["genre"], r["prompt_id"]))
        except Exception:
            pass
    return done


def record(rec):
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def work(model, todo):
    for genre, pid, prompt in todo:
        resp = None
        for attempt in range(MAX_ATTEMPTS.get(model, 3)):
            resp = call(model, prompt, max_tokens=MAX_TOKENS.get(model, 600))
            if resp.get("ok") and (resp.get("content") or "").strip():
                break
            if "429" in (resp.get("error") or ""):
                time.sleep(20)  # free-tier rate window: back off before retry
            else:
                time.sleep(3)
        ok = resp.get("ok") and (resp.get("content") or "").strip()
        rec = {"model": model, "genre": genre, "prompt_id": pid, "prompt": prompt,
               "output": resp.get("content") if ok else f"[FAIL {(resp.get('error') or 'empty')[:100]}]",
               "usage": resp.get("usage"), "cost": None,
               "finish": resp.get("finish"), "ok": ok,
               "price0_verified": True, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        try:
            cost = getattr(resp.get("usage"), "cost", None)
            rec["cost"] = cost
        except Exception:
            pass
        record(rec)
        with _stats_lock:
            _stats["ok" if ok else "fail"] += 1
        print(f"[{model[:24]:24s}] {genre:6s} {pid:4s} ok={ok} "
              f"tok={rec['usage'] and rec['usage'].get('total_tokens')}", flush=True)


def main():
    import sys as _sys
    models = _sys.argv[1:] or DEFAULT_MODELS
    assert_unprimed()
    verify_free(models)
    done = load_done()
    todo_all = [(m, [(g, p, t) for (g, p, t) in PROMPTS if (m, g, p) not in done])
                for m in models]
    total_new = sum(len(t) for _, t in todo_all)
    print(f"[todo] {total_new} new generations across {len(models)} models")
    if total_new == 0:
        print("nothing to do — all records already present")
        return
    threads = []
    for m, todo in todo_all:
        th = threading.Thread(target=work, args=(m, todo), daemon=True)
        threads.append(th)
        th.start()
    for th in threads:
        th.join()
    ok_n = sum(1 for _ in open(OUT, encoding="utf-8") if '"ok": true' in _ and _)
    print(f"DONE ok={_stats['ok']} fail={_stats['fail']} skipped={_stats['skip']} "
          f"| total ok lines now {ok_n}")


if __name__ == "__main__":
    main()