# RY3 v03 Campaign — Full Handoff for Mira

**Date:** 2026-10-13 ~01:40 CDT
**From:** WR3N (via Ryan)
**Purpose:** Complete record of the v03 campaign — both training runs, both evaluations, the diagnosis, and the v02 weakness map — so you can analyze and co-design Dataset 4 with Ryan.

---

## 1. Campaign state

- **Champion: v02** — 19.57/20 on the locked 240-example repaired eval (240/240 parsed). v02 vs base: +8.5%. v02 vs v01: +8.7%.
- **Base:** 18.03/20. **v01:** 18.00/20 (237/240 parsed; 3 parse failures excluded from means).
- **v03: NO-GO, twice.** v02 remains champion. Rule in force: **never continue training from a failed adapter.**

## 2. v03 training — Run 1 (Kaggle, DEVIATED)

- 2026-10-12 ~18:11 UTC. 2x T4 GPUs, ~4.5 min.
- **Deviation:** ran **22 optimizer steps instead of 44** — 2 GPUs doubled the effective batch to 32, halving the step count. (Config A specified 44 steps, batch 16, 2 epochs.)
- Final loss: **8.995** (vs v02's 0.43 — the warning sign).
- Adapter: 158MB, saved and verified, full local copy held.

## 3. v03 training — Run 2 (Colab paid T4, TRUE 44-step)

- 2026-10-12 ~22:31 UTC. Single T4, paid compute ($9.99 / 100 units, pay-as-you-go, 90-day expiry — sponsored by Ryan's mother).
- **44/44 steps, 2 epochs.** Final loss: **3.789.** Healthy descending loss curve (4.840 → 2.757). `V03_TRAINING_SAVED` confirmed.
- Saved to Drive: `My Drive/RY3/RY3_QWEN3_1.7B_v03_44step`
- Script: `eval_repair/v03_train_configA_44step.py`. Dataset: 349 examples (`dataset3.jsonl`).

## 4. Evaluation — Run 1 (22-step adapter)

- 2026-10-12 ~21:19 UTC. Locked 240-example test, same judge config as the repaired eval (Qwen3-1.7B, max_new_tokens=1024, think-stripping, two-attempt JSON extraction, strict validation, parse failures excluded from means).
- **18.29/20** (gate ≥ 19.4 — FAIL). **75 regressions** vs base (gate ≤ 5 — FAIL). 240/240 parsed.
- Per-criterion (/4): correctness 3.758, relevance 3.725, completeness 3.458, instruction_following 3.800, reasoning_quality 3.550.

## 5. Evaluation — Run 2 (true 44-step adapter)

- 2026-10-13 ~06:01 UTC (01:01 CDT). Same locked test and gates. First attempt's browser session died mid-run and its outputs were lost; relaunched with a hardened script writing results/judgments **directly to Drive** (`My Drive/RY3/eval_44step/`, resume-safe).
- **17.18/20** (gate ≥ 19.4 — FAIL). **110 regressions** vs base (gate ≤ 5 — FAIL). 240/240 parsed.
- Per-criterion (/4): correctness 3.517, relevance 3.546, completeness 3.117, instruction_following 3.688, reasoning_quality 3.312.
- Worst regressions: RY3-ULTRA-01367 (−20), RY3-ULTRA-01029 (−16), RY3-ULTRA-01373 (−11), RY3-ULTRA-00536 (−10), RY3-ULTRA-01646 (−8).

## 6. Diagnosis — the dose-response

**44 steps scored LOWER than 22 steps: 17.18 vs 18.29.** More training on Dataset 3 = more degradation. This rules out step count as the cause and confirms the prime suspect:

- **Dataset 3's heavy format drilling degraded content quality.** Completeness fell across the campaign: v02 3.879 → 22-step 3.458 → 44-step 3.117. Reasoning quality fell: v02 3.804 → 3.550 → 3.312.
- The model learned D3's format at the expense of substance. Training loss looked healthy (3.789); eval exposed it. Loss is not the metric — the locked eval is.

## 7. v02 weakness map (headroom for Dataset 4)

From the 240 prior judgments (independently re-verified 2026-10-13):

| Criterion | v02 mean (/4) | Sub-4 scores |
|---|---|---|
| correctness | 3.979 | 4 |
| relevance | 3.954 | 9 |
| instruction_following | 3.954 | 9 |
| completeness | 3.879 | 24 |
| reasoning_quality | **3.804** | **39** |

- Score distribution: 194 perfect (20/20), 21 at 19, 11 at 18, 5 at 17, 6 at 16, 2 at 14, 1 at 11.
- v02 trails base on only 19 examples (worst: −4 on RY3-ULTRA-01814, RY3-ULTRA-01583).
- **The failure pattern in v02's 46 imperfect scores:** "repeats the reference answer without adding new information," "misses the tradeoff between positive/negative feedback and delays," "lacks comparison of alternatives and tradeoffs." Correctness is nearly maxed — the headroom is **depth of reasoning and completeness of coverage**, not factual accuracy.

## 8. Recommended Dataset 4 design principles (WR3N's take — for your analysis)

1. **Target reasoning_quality and completeness only** — the two criteria with real headroom. Examples should demand multi-perspective reasoning, tradeoff analysis, comparison of alternatives.
2. **No format drilling.** D3 proved format-heavy data degrades content. Format compliance is already solved; do not re-teach it.
3. **Failure-mode-driven curation:** mine v02's 46 imperfect scores + the 19 where v02 trails base. Build D4 examples from those exact failure shapes.
4. **Small and excellent over large and drilled.** Quality per example matters more than count — v02's recipe (Datasets 1+2) worked; D4 should extend it, not replace it.
5. **Keep the gates:** mean ≥ 19.4/20, regressions ≤ 5, parse failures excluded from means, never silently zeroed.

## 9. File locations

- `eval_repair/RY3_EVAL_REPAIR_judgments.jsonl` — 720 prior judgments (base/v01/v02)
- `eval_repair/RY3_EVAL_REPAIR.ipynb` — repaired eval notebook
- `eval_repair/dataset3.jsonl` — the 349-example Dataset 3 (the poison)
- `eval_repair/v03_train_configA_44step.py` — true 44-step training script
- `eval_repair/v03_44step_eval_colab.py` — eval script (Drive-writing, resume-safe)
- `eval_repair/results_44step/v03_44step_judgments.jsonl` — 240 v03 judgments (local copy)
- `eval_repair/results_44step/v03_44step_results.jsonl` — 240 v03 generations (local copy)
- Drive: `My Drive/RY3/eval_44step/` — results + judgments (Drive copy)
- Drive: `My Drive/RY3/RY3_QWEN3_1.7B_v03_44step` — the 44-step adapter (Restricted)
- Drive: `My Drive/RY3/v03_inputs` — re-locked to Restricted 2026-10-13 per Ryan

## 10. Open questions for you and Ryan

- D4 size and composition (recommendation: small, targeted, §8).
- Whether to train D4 from the v02 adapter (continuation) or from base.
- Judge calibration: v02's 19.57 may be near the judge's noise ceiling — worth discussing how to distinguish real gains from judge variance at the top end.
