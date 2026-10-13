#!/usr/bin/env python3
"""
RY3 v03_44step evaluation — standalone Colab GPU script (paid T4).

Does on a Colab notebook (paid T4 GPU, Drive mounted):
  Phase 1: loads base saidutta69/Qwen3-1.7B-heretic (4-bit NF4) + v03_44step LoRA adapter
           from Drive, generates one response per eval instruction (same generation
           params the v01/v02 evals used: max_new_tokens=200, temp 0.7, top_p 0.8,
           top_k 20).
  Phase 2: judges every v03 response with Qwen/Qwen3-1.7B (clean base, bf16) using
           the EXACT repaired judge logic from RY3_EVAL_REPAIR.ipynb
           (max_new_tokens=1024, temp 0.1, strip <think> before JSON parse,
           parse failures recorded as parsed=False — NEVER zeroed).
  Phase 3: prints the scoreboard + GO/NO-GO vs the bar (mean >= 19.4/20,
           regressions vs base <= 5).

COLAB SETUP (run in notebook cells before this script):
  # Runtime -> Change runtime type -> T4 GPU (paid compute units)
  !pip install -q transformers peft datasets bitsandbytes accelerate
  # mount Drive; the v03_44step adapter is already at
  #   /content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v03_44step (no download needed)
  # upload eval_instructions.jsonl (240 rows: id, instruction, expected)
  #   and prior_judgments.jsonl (720 rows: base/v01/v02) to /content/
  !python /content/v03_44step_eval_colab.py

Outputs:
  /content/v03_44step_results.jsonl    (id, instruction, expected, response)
  /content/v03_44step_judgments.jsonl  (same schema as RY3_EVAL_REPAIR_judgments.jsonl,
                                        model="v03")
Both phases are resume-safe: eval IDs already on disk are skipped.
The 240 eval instructions are read as-is and never modified.
"""

import collections
import gc
import json
import os
import re

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
BASE_MODEL = "saidutta69/Qwen3-1.7B-heretic"   # candidate base (v03 adapter's base)
JUDGE_MODEL = "Qwen/Qwen3-1.7B"               # judge: CLEAN base, per project convention

V03_ADAPTER_DIR = "/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v03_44step"
EVAL_INSTRUCTIONS = "/content/eval_instructions.jsonl"
PRIOR_JUDGMENTS = "/content/prior_judgments.jsonl"
# Outputs go DIRECTLY to Drive (not /content/) so results survive a Colab
# runtime/browser-session death. JSONL appends are tiny; Drive FUSE handles them.
# Resume-safe across restarts: already-scored IDs are skipped on re-run.
DRIVE_OUT_DIR = "/content/drive/MyDrive/RY3/eval_44step"
os.makedirs(DRIVE_OUT_DIR, exist_ok=True)
V03_RESULTS = os.path.join(DRIVE_OUT_DIR, "v03_44step_results.jsonl")
V03_JUDGMENTS = os.path.join(DRIVE_OUT_DIR, "v03_44step_judgments.jsonl")

# Candidate-response generation params — identical to the v01/v02 eval
# generation (Untitled2.ipynb cells 49/50/81).
GEN_MAX_NEW_TOKENS = 200
GEN_TEMPERATURE = 0.7
GEN_TOP_P = 0.8
GEN_TOP_K = 20

# Repaired-judge params (RY3_EVAL_REPAIR.ipynb cells 10/12).
JUDGE_MAX_NEW_TOKENS = 1024
JUDGE_TEMPERATURE = 0.1

# GO/NO-GO bar set by Ryan (2026-10-12).
GO_MEAN_BAR = 19.4
GO_MAX_REGRESSIONS = 5

# ----------------------------------------------------------------------------
# Judge prompt — VERBATIM from RY3_EVAL_REPAIR.ipynb cell 10.
# NOTE (flagged, not changed): the notebook's comment claims "the system prompt
# explicitly forbids think tags", but the actual JUDGE_SYSTEM string below
# contains no explicit <think> prohibition. The operative defense is the
# post-hoc _strip_think() before JSON extraction (cell 14). Kept as-is.
# ----------------------------------------------------------------------------
JUDGE_SYSTEM = """You are an impartial evaluator. Your job is to grade an AI assistant's response to a user instruction.
You MUST output ONLY a single JSON object with exactly these keys:
- "correctness": integer 0-4
- "relevance": integer 0-4
- "completeness": integer 0-4
- "instruction_following": integer 0-4
- "reasoning_quality": integer 0-4
- "brief_reason": one short sentence explaining the scores
Rubric for each 0-4 dimension: 0 = total failure, 1 = poor, 2 = acceptable, 3 = good, 4 = excellent.
STRICT RULES: Output ONLY the JSON object. No prose before or after it. No markdown code fences. No explanations outside the JSON. Start your output with { and end it with }."""


def build_judge_messages(item):
    user = (
        "INSTRUCTION GIVEN TO THE ASSISTANT:\n" + item["instruction"] +
        "\n\nREFERENCE (EXPECTED) ANSWER:\n" + item["expected"] +
        "\n\nASSISTANT'S ACTUAL RESPONSE:\n" + item["response"] +
        "\n\nGrade the assistant's response on the five dimensions. Output ONLY the JSON object."
    )
    return [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": user},
    ]


# ----------------------------------------------------------------------------
# Robust parser — VERBATIM from RY3_EVAL_REPAIR.ipynb cell 14.
# Parse failures are recorded as parsed=False WITH the raw output.
# They are NEVER turned into fake zero scores.
# ----------------------------------------------------------------------------
REQUIRED_KEYS = ["correctness", "relevance", "completeness",
                 "instruction_following", "reasoning_quality", "brief_reason"]
SCORE_KEYS = REQUIRED_KEYS[:5]

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_think(text):
    """Remove Qwen3 <think> reasoning blocks before JSON extraction."""
    return _THINK_RE.sub("", text).strip()


def parse_judge_output(raw, eval_id, model_name):
    raw = _strip_think(raw)
    rec = {"eval_id": eval_id, "model": model_name}

    def fail(reason):
        rec.update({"parsed": False, "parse_error": reason, "raw_judge_output": raw})
        return rec

    data = None
    try:
        data = json.loads(raw)                    # attempt 1: strict parse
    except Exception:
        m = re.search(r"\{.*\}", raw, re.DOTALL)   # attempt 2: first {...} block
        if not m:
            return fail("no JSON object found in judge output")
        try:
            data = json.loads(m.group(0))
        except Exception as e:
            return fail(f"JSON decode failed after brace extraction: {e}")

    if not isinstance(data, dict):
        return fail("parsed JSON is not an object")
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        return fail(f"missing required keys: {missing}")
    for k in SCORE_KEYS:
        v = data[k]
        if isinstance(v, bool) or not isinstance(v, int):
            return fail(f"score '{k}' is not an integer: {v!r}")
        if not (0 <= v <= 4):
            return fail(f"score '{k}' out of range 0-4: {v}")
    brief = data["brief_reason"]
    if not isinstance(brief, str) or not brief.strip():
        return fail("brief_reason is not a non-empty string")

    rec.update({
        "parsed": True,
        "correctness": data["correctness"],
        "relevance": data["relevance"],
        "completeness": data["completeness"],
        "instruction_following": data["instruction_following"],
        "reasoning_quality": data["reasoning_quality"],
        "brief_reason": brief.strip(),
        "raw_judge_output": raw,
    })
    return rec


def _self_test_parser():
    # Mirrors the parser unit tests in RY3_EVAL_REPAIR.ipynb cell 14.
    _good = '{"correctness": 3, "relevance": 4, "completeness": 3, "instruction_following": 4, "reasoning_quality": 2, "brief_reason": "Clear and on-topic."}'
    assert parse_judge_output(_good, "x", "v03")["parsed"] is True
    _thinky = '<think>Let me think... the answer looks good.</think>\n' + _good
    assert parse_judge_output(_thinky, "x", "v03")["parsed"] is True
    _bad = parse_judge_output("The response is pretty good overall.", "x", "v03")
    assert _bad["parsed"] is False and "raw_judge_output" in _bad and "parse_error" in _bad
    _oob = parse_judge_output('{"correctness": 9, "relevance": 4, "completeness": 3, "instruction_following": 4, "reasoning_quality": 2, "brief_reason": "x"}', "x", "v03")
    assert _oob["parsed"] is False
    print("parser self-tests passed", flush=True)


# ----------------------------------------------------------------------------
# Scoreboard — pure python (no torch), same methodology as the repair:
# means computed over PARSED judgments only; failures excluded, never zeroed.
# ----------------------------------------------------------------------------
def compute_scoreboard(v03_judgments, prior_judgments):
    ok = [j for j in v03_judgments if j.get("parsed")]
    n = len(v03_judgments)
    n_ok = len(ok)
    totals = [sum(j[k] for k in SCORE_KEYS) for j in ok]
    mean_total = sum(totals) / len(totals) if totals else None
    crit_means = {k: (sum(j[k] for j in ok) / len(ok) if ok else None) for k in SCORE_KEYS}

    base_score = {}
    for j in prior_judgments:
        if j.get("model") == "base" and j.get("parsed"):
            base_score[j["eval_id"]] = sum(j[k] for k in SCORE_KEYS)
    v03_score = {j["eval_id"]: sum(j[k] for k in SCORE_KEYS) for j in ok}

    regressions = []
    for eid, v in sorted(v03_score.items()):
        b = base_score.get(eid)
        if b is not None and v < b:
            regressions.append({"eval_id": eid, "base": b, "v03": v, "delta": v - b})

    go_mean = mean_total is not None and mean_total >= GO_MEAN_BAR
    go_reg = len(regressions) <= GO_MAX_REGRESSIONS
    return {
        "n": n,
        "parsed": n_ok,
        "parse_rate": 100.0 * n_ok / n if n else 0.0,
        "mean_total": mean_total,
        "criterion_means": crit_means,
        "regressions": regressions,
        "n_regressions": len(regressions),
        "go_mean": go_mean,
        "go_regressions": go_reg,
        "verdict": "GO" if (go_mean and go_reg) else "NO-GO",
    }


def format_scoreboard(rep):
    L = []
    L.append("=" * 64)
    L.append("RY3 v03 EVAL SCOREBOARD")
    L.append("=" * 64)
    L.append(f"judgments: {rep['parsed']}/{rep['n']} parsed ({rep['parse_rate']:.1f}%)")
    mt = rep["mean_total"]
    L.append(f"v03 mean total: {mt:.2f}/20" if mt is not None else "v03 mean total: n/a (no parsed judgments)")
    L.append("")
    L.append(f"{'criterion':<22}{'mean /4':>8}")
    for k in SCORE_KEYS:
        v = rep["criterion_means"][k]
        L.append(f"{k:<22}{v:>8.3f}" if v is not None else f"{k:<22}{'n/a':>8}")
    L.append("")
    L.append(f"regressions vs base (v03 < base): {rep['n_regressions']}")
    for r in rep["regressions"]:
        L.append(f"  {r['eval_id']:<28} base={r['base']:>2} v03={r['v03']:>2} (delta {r['delta']:+d})")
    L.append("")
    L.append(f"gate 1 — mean >= {GO_MEAN_BAR}/20:            {'PASS' if rep['go_mean'] else 'FAIL'}")
    L.append(f"gate 2 — regressions <= {GO_MAX_REGRESSIONS}:            {'PASS' if rep['go_regressions'] else 'FAIL'}")
    L.append("")
    L.append(f"VERDICT: {rep['verdict']}")
    L.append("=" * 64)
    return "\n".join(L)


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                # torn write from a crashed run — skip; the id will be redone
                print(f"warning: skipping unparseable line in {path}", flush=True)
    return rows


def main():
    import torch
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              BitsAndBytesConfig)
    from peft import PeftModel

    print("v03 eval starting", flush=True)
    _self_test_parser()

    # ---- validate inputs (fail loudly) ----
    assert os.path.isdir(V03_ADAPTER_DIR), f"v03_44step adapter dir missing: {V03_ADAPTER_DIR}"
    has_weights = os.path.isfile(os.path.join(V03_ADAPTER_DIR, "adapter_model.safetensors")) or \
                  os.path.isfile(os.path.join(V03_ADAPTER_DIR, "adapter_model.bin"))
    assert has_weights, f"no adapter_model.safetensors/.bin in {V03_ADAPTER_DIR}"
    assert os.path.isfile(os.path.join(V03_ADAPTER_DIR, "adapter_config.json")), \
        f"no adapter_config.json in {V03_ADAPTER_DIR}"
    assert os.path.isfile(EVAL_INSTRUCTIONS), f"eval instructions missing: {EVAL_INSTRUCTIONS}"
    assert os.path.isfile(PRIOR_JUDGMENTS), f"prior judgments missing: {PRIOR_JUDGMENTS}"
    print("inputs validated", flush=True)

    instructions = load_jsonl(EVAL_INSTRUCTIONS)
    for r in instructions:
        assert {"id", "instruction", "expected"} <= set(r.keys()), f"bad instruction row keys: {sorted(r.keys())}"
    ids = [r["id"] for r in instructions]
    assert len(ids) == len(set(ids)) == 240, f"expected 240 unique eval ids, got {len(instructions)} rows / {len(set(ids))} unique"
    print(f"loaded {len(instructions)} eval instructions (locked set, read-only)", flush=True)

    def _dev(m):
        try:
            return m.device
        except Exception:
            pass
        try:
            return next(m.parameters()).device
        except Exception:
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ================= Phase 1: generate v03 responses =================
    print("phase 1: loading candidate (heretic 4-bit + v03 adapter)...", flush=True)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_use_double_quant=True,
                             bnb_4bit_compute_dtype=torch.float16)
    cand_base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, quantization_config=bnb, device_map="auto", trust_remote_code=True)
    cand_model = PeftModel.from_pretrained(cand_base, V03_ADAPTER_DIR, is_trainable=False)
    cand_model.eval()
    cand_tok = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if cand_tok.pad_token is None:
        cand_tok.pad_token = cand_tok.eos_token
    print("candidate loaded", flush=True)

    def gen_response(instruction):
        messages = [{"role": "user", "content": instruction}]
        try:
            prompt = cand_tok.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        except TypeError:
            prompt = cand_tok.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True)
        inputs = cand_tok(prompt, return_tensors="pt").to(_dev(cand_model))
        with torch.no_grad():
            out = cand_model.generate(
                **inputs,
                max_new_tokens=GEN_MAX_NEW_TOKENS,
                do_sample=True,
                temperature=GEN_TEMPERATURE,
                top_p=GEN_TOP_P,
                top_k=GEN_TOP_K,
                pad_token_id=cand_tok.eos_token_id,
            )
        gen_ids = out[0][inputs["input_ids"].shape[1]:]
        return cand_tok.decode(gen_ids, skip_special_tokens=True).strip()

    done_resp = {}
    if os.path.exists(V03_RESULTS):
        for r in load_jsonl(V03_RESULTS):
            done_resp[r["id"]] = r
        print(f"phase 1 resume: {len(done_resp)} responses already on disk", flush=True)

    n_new = 0
    with open(V03_RESULTS, "a", encoding="utf-8") as f:
        for i, ex in enumerate(instructions, 1):
            if ex["id"] in done_resp:
                continue
            resp = gen_response(ex["instruction"])
            f.write(json.dumps({"id": ex["id"], "instruction": ex["instruction"],
                                "expected": ex["expected"], "response": resp},
                               ensure_ascii=False) + "\n")
            f.flush()
            n_new += 1
            if n_new % 20 == 0:
                print(f"[gen {i}/240] new={n_new}", flush=True)
    print(f"phase 1 done: {n_new} new responses ({len(done_resp) + n_new}/240 total)", flush=True)

    # free the candidate before loading the judge
    del cand_model, cand_base, cand_tok
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # ================= Phase 2: judge with repaired logic =================
    print(f"phase 2: loading judge {JUDGE_MODEL} (bf16)...", flush=True)
    judge_tok = AutoTokenizer.from_pretrained(JUDGE_MODEL)
    judge_model = AutoModelForCausalLM.from_pretrained(
        JUDGE_MODEL, torch_dtype=torch.bfloat16, device_map="auto")
    judge_model.eval()
    print("judge loaded", flush=True)

    def render_prompt(messages):
        try:
            return judge_tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception:
            parts = [f"{m['role'].upper()}:\n{m['content']}" for m in messages]
            return "\n\n".join(parts) + "\n\nASSISTANT:\n"

    def judge_generate(messages):
        prompt = render_prompt(messages)
        inputs = judge_tok([prompt], return_tensors="pt").to(_dev(judge_model))
        with torch.no_grad():
            out = judge_model.generate(
                **inputs,
                max_new_tokens=JUDGE_MAX_NEW_TOKENS,
                temperature=JUDGE_TEMPERATURE,
                do_sample=JUDGE_TEMPERATURE > 0,
                pad_token_id=judge_tok.eos_token_id,
            )
        gen_ids = out[0][inputs["input_ids"].shape[1]:]
        return judge_tok.decode(gen_ids, skip_special_tokens=True).strip()

    def run_judge(item):
        raw = judge_generate(build_judge_messages(item))
        return parse_judge_output(raw, item["eval_id"], item["model"])

    results_by_id = {r["id"]: r for r in load_jsonl(V03_RESULTS)}
    assert len(results_by_id) == 240, f"expected 240 v03 responses, have {len(results_by_id)}"

    done_j = set()
    if os.path.exists(V03_JUDGMENTS):
        for r in load_jsonl(V03_JUDGMENTS):
            done_j.add((r["eval_id"], r["model"]))
        print(f"phase 2 resume: {len(done_j)} judgments already on disk", flush=True)

    fails = judged = 0
    with open(V03_JUDGMENTS, "a", encoding="utf-8") as f:
        for i, ex in enumerate(instructions, 1):
            if (ex["id"], "v03_44step") in done_j:
                continue
            r = results_by_id[ex["id"]]
            item = {"eval_id": ex["id"], "model": "v03_44step",
                    "instruction": ex["instruction"], "expected": ex["expected"],
                    "response": r["response"]}
            rec = run_judge(item)
            judged += 1
            if not rec["parsed"]:
                fails += 1
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()  # write-as-you-go: a crash loses nothing already judged
            if judged % 20 == 0:
                print(f"[judge {i}/240] judged={judged} parse_failures={fails} "
                      f"({fails / max(judged, 1) * 100:.1f}%)", flush=True)
    print(f"phase 2 done: {judged} new judgments, {fails} parse failures", flush=True)

    # ================= Phase 3: scoreboard + GO/NO-GO =================
    v03_judgments = load_jsonl(V03_JUDGMENTS)
    prior = load_jsonl(PRIOR_JUDGMENTS)
    rep = compute_scoreboard(v03_judgments, prior)
    print(format_scoreboard(rep), flush=True)
    print("V03_EVAL_DONE", flush=True)


if __name__ == "__main__":
    main()
