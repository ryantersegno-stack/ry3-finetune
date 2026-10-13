# RY3 D4 Shot 1 — Experiment Brief

**Status:** In progress as of 2026-10-13
**Designers:** Rye + Mira
**Execution:** WR3N (execution engine)

## Objective

Test whether the curated D4 dataset repairs v02's measured structural
instruction-following weaknesses **without sacrificing the substantive
quality that made v02 the champion** (19.57/20).

This is NOT a formatting-drill experiment. D3's failure (see below) proved
that format-heavy training degrades content quality.

## Background: why D4 exists

v02's weakness map (from 240 locked-benchmark judgments):

| Criterion | v02 mean (/4) | Sub-4 scores |
|---|---|---|
| correctness | 3.979 | 4 |
| relevance | 3.954 | 9 |
| instruction_following | 3.954 | 9 |
| completeness | 3.879 | 24 |
| reasoning_quality | **3.804** | **39** |

The failure pattern in v02's 46 imperfect scores: shallow reasoning, missing
tradeoffs, no comparison of alternatives. Correctness is nearly maxed — the
headroom is depth of reasoning and completeness of coverage.

D3 attempted to fix this with 349 format-obedience examples. Two runs:
- 22-step run: 18.29/20, 75 regressions vs base → NO-GO
- 44-step run: 17.18/20, 110 regressions vs base → NO-GO

The 44-step run scoring LOWER than the 22-step run is the key evidence:
more training on Dataset 3 = more degradation (completeness 3.879 → 3.117).
Dose-response proves D3's format drilling was the poison, not the step count.

## D4 dataset

- **File:** `data/RY3_Dataset4_FIXED.jsonl`
- **SHA256:** `e4d026639da2671f8c71c7abaae38297ca34ce02841a69792e988af3c418b846`
- **Size:** 160 examples (validated: 160/160 unique instruction+output pairs,
  0 duplicates, 0 malformed, schema verified)
- **Distribution:** 40 compare_tradeoff / 40 troubleshoot_steps /
  40 concise_keychecks / 20 explain_example / 20 other+meta_reasoning
- **Design principle:** content and reasoning first; target structures
  (ordered troubleshooting steps, key checks, tradeoff analysis, concrete
  examples, fresh generation) demonstrated naturally inside high-quality
  answers — never drilled as isolated templates.

A first D4 file supplied was defective (17 unique pairs cloned to 160
records). It was caught in validation, quarantined, and never used.

## Locked training configuration (Shot 1)

- **Starting checkpoint:** v02 (`RY3_QWEN3_1.7B_v02`)
- **Base model:** saidutta69/Qwen3-1.7B-heretic (4-bit NF4)
- **Dataset:** RY3_Dataset4_FIXED.jsonl (SHA256-verified before training)
- **Epochs:** 1
- **Learning rate:** 5e-5
- **Effective batch size:** 16 (per-device 2 × grad-accum 8)
- **Optimizer:** paged_adamw_8bit
- **Precision:** fp32
- **Gradient checkpointing:** enabled
- **LoRA:** r=16, alpha=32, dropout=0.05, targets q/k/v/o/gate/up/down_proj
  (continues v02's adapter weights directly; v02 adapter_config verified
  r=16/alpha=32/dropout=0.05, same 7 targets)
- **Seed:** 42, **max length:** 2048, **warmup:** 0 (library default)

160 examples / eff batch 16 = **10 optimizer steps**.

## Evaluation plan

After training, evaluate on the SAME locked 240-example benchmark:
1. Base
2. v02
3. D4 Shot 1

Judge: Qwen3-1.7B, 5 criteria × 0–4, strict JSON validation, parse
failures excluded from means and never converted to zero.

## Promotion gates

- Mean ≥ 19.4/20 **AND** ≤ 5 regressions vs base
- v02 (19.57) remains champion until beaten
- D4 is NOT successful merely because instruction-following increases —
  substantive quality (correctness, relevance, completeness, reasoning)
  must be preserved or improved

## Training script

`training/d4_train_shot1.py` — asserts dataset SHA256 before training,
records full effective config to `D4_SHOT1_TRAINING_REPORT.json`.
