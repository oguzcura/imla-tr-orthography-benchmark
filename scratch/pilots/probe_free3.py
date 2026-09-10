# -*- coding: utf-8 -*-
"""probe_free3.py — live re-probe of OpenRouter :free (price==0) endpoints for Imla full study.

1) Lists ALL price==0 endpoints right now.
2) Probes candidates: short call (empty check) + 100-word Turkish news gen (finish check,
   Turkish output check, meta-narration check).
Only endpoints verified price==0 from the live listing are eligible; run refuses others.
"""
import json, os, sys, time, urllib.request, urllib.parse
from openai import OpenAI

def load_secret(name):
    v = os.getenv(name)
    if v:
        return v
    for line in open(r"C:\Users\oguzc\AppData\Local\hermes\.env", encoding="utf-8"):
        line = line.strip()
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

KEY = load_secret("OPENROUTER_API_KEY")
BASE = "https://openrouter.ai/api/v1"

def live_free_models():
    req = urllib.request.Request(BASE + "/models", headers={"Authorization": f"Bearer {KEY}"})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    rows = []
    for m in d.get("data", []):
        p = m.get("pricing") or {}
        pr = float(p.get("prompt") or 0); co = float(p.get("completion") or 0)
        if pr == 0 and co == 0:
            rows.append({"id": m["id"], "name": (m.get("name") or "")[:70],
                         "ctx": m.get("context_length")})
    return rows

def call(model, user, max_tokens=600, timeout=120, attempts=2):
    client = OpenAI(base_url=BASE, api_key=KEY, timeout=timeout, max_retries=1)
    for a in range(attempts):
        t0 = time.time()
        try:
            r = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": user}],
                max_tokens=max_tokens, temperature=0)
            msg = r.choices[0].message
            content = (msg.content or "").strip()
            u = r.usage
            usage = {"prompt_tokens": getattr(u, "prompt_tokens", None),
                     "completion_tokens": getattr(u, "completion_tokens", None),
                     "total_tokens": getattr(u, "total_tokens", None)}
            return {"ok": (len(content) > 0), "content": content, "usage": usage,
                    "finish": r.choices[0].finish_reason,
                    "took_s": round(time.time() - t0, 1)}
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:200]}"
            time.sleep(2)
    return {"ok": False, "content": "", "finish": None, "error": err if "err" in dir() else "fail"}

TURKISH_CHARS = set("ğışçöüİĞŞÇÖÜ")

def main():
    free = live_free_models()
    print(f"[live] {len(free)} price==0 endpoints on OpenRouter right now:")
    for f in free:
        print("   ", f["id"])
    if len(sys.argv) > 1:
        candidates = sys.argv[1:]
    else:
        candidates = [
            "google/gemma-4-31b-it:free",
            "google/gemma-4-26b-a4b-it:free",
            "minimax/minimax-m3:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-small-3.2-24b-instruct:free",
            "qwen/qwen3-32b:free",
            "deepseek/deepseek-chat-v3-0324:free",
            "openai/gpt-oss-120b:free",
            "z-ai/glm-4.5-air:free",
            "moonshotai/kimi-k2-instruct:free",
        ]
    ids = {f["id"] for f in free}
    out = {}
    for m in candidates:
        if m not in ids:
            print(f"\n== {m}: NOT price==0 in live listing, skipped")
            out[m] = {"eligible": False}
            continue
        print(f"\n== PROBE {m}")
        s = call(m, "1+1=? Tek kelime cevap ver.", max_tokens=20)
        print("   short:", "OK" if s["ok"] else "EMPTY/FAIL", repr((s.get("content") or "")[:40]), s.get("finish"))
        if not s["ok"]:
            out[m] = {"eligible": True, "short_ok": False, "error": s.get("error")}
            continue
        n = call(m, "Bir haber ajansı üslubuyla, Türkçe, İstanbul'da kuvvetli rüzgar nedeniyle feribot seferlerinin aksadığı günü anlatan 100 kelimelik bir haber metni yaz.", max_tokens=500)
        cont = n.get("content") or ""
        tr_ratio = sum(1 for c in cont if c in TURKISH_CHARS) / max(1, len(cont))
        meta = any(x in cont.lower() for x in ["here is", "sure,", "i will write", "certainly", "as a language model"])
        print(f"   news: ok={n['ok']} finish={n.get('finish')} tokens={n.get('usage') and n['usage'].get('total_tokens')} "
              f"tr_chars/len={tr_ratio:.3f} meta={meta} err={n.get('error','')}")
        print("   head:", repr(cont[:150]))
        out[m] = {"eligible": True, "short_ok": True, "finish": n.get("finish"),
                  "tr_ratio": round(tr_ratio, 3), "meta_narration": meta, "news_ok": n["ok"],
                  "tokens": n.get("usage") and n["usage"].get("total_tokens")}
        time.sleep(0.3)
    print("\n=== SUMMARY ===")
    for m, r in out.items():
        if not r.get("eligible"):
            print(f"  {m:45s} NOT-FREE")
        elif not r.get("short_ok"):
            print(f"  {m:45s} EMPTY-RATE FAIL")
        elif not r.get("news_ok") or r.get("finish") != "stop":
            print(f"  {m:45s} NEWS FAIL finish={r.get('finish')}")
        elif r.get("meta_narration"):
            print(f"  {m:45s} META-NARRATION")
        else:
            print(f"  {m:45s} PASS (tr={r.get('tr_ratio')}, {r.get('tokens')} tok)")
    with open("probe_free3_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("saved probe_free3_results.json")

if __name__ == "__main__":
    main()