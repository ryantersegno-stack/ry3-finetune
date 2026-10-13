# RY3 — Fine-Tuning Qwen3-1.7B with LoRA

Personal ML experimentation project by **Ryan (KING_RY3)**: fine-tuning
`saidutta69/Qwen3-1.7B-heretic` with LoRA adapters, driven by a locked
evaluation benchmark and promotion gates. Every claim below is backed by
the judgments, results, and scripts in this repo.

## The evaluation

All models are scored on the **same locked 240-example benchmark**
(`data/eval_instructions_240_locked.jsonl`) by a **Qwen3-1.7B judge** on
five criteria, each 0–4:

- correctness · relevance · completeness · instruction_following · reasoning_quality

Judge protocol: strict JSON validation, two-attempt extraction, parse
failures are **excluded from means** and never silently converted to zero.
A parser failure is an evaluation failure, not a model score.

## Scoreboard (verified)

| Model | Mean /20 | Parse rate | Regressions vs base | Verdict |
|---|---|---|---|---|
| base | **18.03** | 240/240 | — | baseline |
| v01 | **18.00** | 237/240 | — | — |
| **v02** | **19.57** | 240/240 | — | **champion** (+8.5% vs base) |
| v03 (22-step) | 18.29 | 240/240 | 75 | **NO-GO** |
| v03 (44-step) | 17.18 | 240/240 | 110 | **NO-GO** |

Promotion gates: mean **≥ 19.4/20** AND **≤ 5 regressions** vs base.
v02 remains champion until beaten.

## Key scientific finding

The true 44-step v03 run scored **lower** than the broken 22-step run
(17.18 vs 18.29). More training on Dataset 3 = more degradation —
completeness fell 3.879 → 3.117 across the runs. This dose-response
**proves Dataset 3's format drilling degraded content quality**; the
step count was never the cause. Training loss looked healthy (3.789);
the locked eval exposed the truth. Loss is not the metric.

## v02 weakness map → D4

From 240 prior judgments: 194 perfect scores. The headroom is
concentrated in two criteria — **reasoning_quality 3.804/4** (39 sub-4)
and **completeness 3.879/4** (24 sub-4) — with a clear pattern: shallow
reasoning, missing tradeoffs, no comparison of alternatives. Correctness
(3.979) is nearly maxed.

**D4 Shot 1** (in progress, 2026-10-13): a 160-example curated dataset
targeting exactly those measured weaknesses — ordered troubleshooting
steps, key checks, tradeoff analysis, concrete examples, fresh generation —
demonstrated inside high-quality answers, never drilled as isolated
templates. See `docs/D4_SHOT1_EXPERIMENT.md`.

## Repo layout

```
configs/    LoRA adapter config, tokenizer config, chat template, trainer state
data/       Datasets, locked eval set, judgments, results, SHA256SUMS.txt
docs/       Session notes, Mira handoffs, validation reports, experiment briefs
notebooks/  RY3_EVAL_REPAIR.ipynb — the repaired evaluation notebook
training/   Training + evaluation scripts (Kaggle & Colab)
```

## Notes

- Adapter weights (`adapter_model.safetensors`, checkpoints) live on
  Google Drive, not in this repo. See `data/SHA256SUMS.txt` for
  integrity hashes of the data files.
- A first D4 dataset file was defective (17 unique pairs cloned to 160
  records). It was caught in validation, quarantined, and never trained
  on. The validated replacement is `data/RY3_Dataset4_FIXED.jsonl`.
- Rule: never continue training from a failed adapter.
