# PRIMER THEORY Experiment — Manifest

**Date:** 2026-10-13
**Status:** DESIGNED — awaiting Ryan's approval for compute spend
**Type:** Causal isolation experiment (NOT an optimization attempt)

## Scientific question

Does v01 causally enable v02's large gain (+1.57, 18.00 → 19.57), despite v01
showing zero standalone measurable improvement over base (18.00 vs 18.03)?

## Design

**Branch A:** BASE → REPRODUCED v01 → v02
**Branch B:** BASE → v02 directly (no v01 stage)

The v02 stage is IDENTICAL between branches. The ONLY variable is whether
the v01 training stage occurs first.

## Key facts established during design

- v01 (1920 examples, lr 1e-4, 3 epochs): 18.00/20 — no gain over base 18.03
- v02 (800 new targeted examples, lr 5e-5, 2 epochs, cumulative 2720): 19.57/20
- v02's 800 new examples: harder difficulty only, focused categories,
  added "concept_preservation" quality dimension, no foundational examples
- Original v01 adapter NOT located — Branch A uses a REPRODUCED v01
- v01 max_length/warmup/seed NOT preserved in records — using v02's values
  (128/100/42) as the most defensible inference, explicitly flagged

## Files

### Datasets (in eval_repair/)
- `dataset_v01_1920.jsonl` — 1920 RY3-ULTRA examples (v01's data)
  SHA256: 324610f73fe1afb7a2eff72811da23b8af587d13c48dfbf964db62f64393198b
- `dataset_v02cumulative_2720.jsonl` — 2720 examples (1920 + 800)
  SHA256: c9b5ffcbee384c3db53cb4c16338f13969716e24b33280aa7c0662feced1f11b

### Training scripts (in eval_repair/)
- `primer_branchA_v01repro_train.py` — Branch A Stage 1 (syntax OK)
- `primer_branchA_v02_train.py` — Branch A Stage 2 (syntax OK)
- `primer_branchB_v02direct_train.py` — Branch B (syntax OK)

### Pre-filled notebooks (in eval_repair/, per Colab automation rules)
- `primer_branchA_notebook.ipynb` — 6 cells, Run All does both stages
- `primer_branchB_notebook.ipynb` — 4 cells, Run All does Branch B

### Output directories (on Drive, isolated from v02 champion)
- `/content/drive/MyDrive/RY3/RY3_PRIMER_A_v01repro`
- `/content/drive/MyDrive/RY3/RY3_PRIMER_A_v02`
- `/content/drive/MyDrive/RY3/RY3_PRIMER_B_v02direct`

## Hyperparameters

| Setting | v01 repro (A-1) | v02 stage (A-2 and B) |
|---|---|---|
| Start | base (fresh LoRA) | A: repro v01 adapter / B: base (fresh LoRA) |
| Dataset | 1920 | 2720 cumulative |
| LR | 1e-4 | 5e-5 |
| Epochs | 3 | 2 |
| Eff batch | 16 | 16 |
| Warmup | 100* | 100 |
| max_length | 128* | 128 |
| Optimizer | paged_adamw_8bit | paged_adamw_8bit |
| Seed | 42* | 42 |
| LoRA | r16/a32/d0.05 | r16/a32/d0.05 (inherited for A-2) |
| Expected steps | ~360 | ~340 |

*Inferred from v02, not recorded for v01.

## Evaluation plan

Full locked eval (240 examples, verbatim judge protocol) on:
1. Reproduced v01 (sanity check — should ≈ 18.00)
2. Branch A final (reproduced v01 → v02)
3. Branch B final (base → v02 direct)

Compare against existing priors: base (18.03), historical v02 (19.57).
Per-criterion tracking on all five dimensions. Regression counts.

## Interpretation

- B ≈ A → v01 was unnecessary
- B > A → v01 was unnecessary or harmful
- A >> B → v01 is a latent primer
- Both ≠ historical v02 → reproducibility issue, investigate first

## Compute estimate

- Branch A: ~700 steps ≈ 47 min L4
- Branch B: ~340 steps ≈ 23 min L4
- 3 full evals ≈ 60-90 min L4
- Total: ~2.5-3 hours L4, ~12-15 compute units

## Rules

- DO NOT optimize either branch after seeing results
- DO NOT touch v02 champion, original datasets, or historical adapters
- If reproduction sanity check fails, STOP and investigate before proceeding
