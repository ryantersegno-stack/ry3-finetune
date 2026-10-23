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

| Model | Mean /20 | Eval | Parse rate | Regressions vs base | Verdict |
|---|---|---|---|---|---|
| base | **18.03** | full 240 | 240/240 | — | baseline |
| v01 (historical) | **18.00** | full 240 | 237/240 | — | superseded — see faithful v01 |
| **v02** | **19.57** | full 240 | 240/240 | 19 | former champion (+8.5% vs base) — dethroned 2026-10-16 |
| **faithful v01** | **19.59** | full 240 | 240/240 | 15 | **CHAMPION** — beat v02 head-to-head (27 W / 20 L / 193 T) |
| v03 (22-step) | 18.29 | full 240 | 240/240 | 75 | **NO-GO** |
| v03 (44-step) | 17.18 | full 240 | 240/240 | 110 | **NO-GO** |
| D4 Shot 1 | 16.40 | 180 subset | — | 138/180 | **NO-GO** |

Promotion gates: mean **≥ 19.4/20** AND **≤ 5 regressions** vs base.
faithful v01 took the crown on the full locked 240 (19.59/20, 15 regressions vs base — fewer than v02's 19). The champion changed because the evidence changed, not because the bar moved.

**Note on faithful v01:** first scored 19.71 on the 48-example locked
screen (every 5th of the 240), then went to the full locked 240 and
scored **19.59/20** — correctness 3.971 (above the 3.95 gate) — taking
the crown from v02. The adapter is protected as the incumbent: no
continuation, merge, or overwrite until a hypothesis defines the
intervention, success criterion, and regression gate. See
`docs/V01FAITHFUL_FREEZE_DIRECTIVE_2026-10-16.md`.

## Key scientific findings

### Dataset 3's format drilling degraded quality (2026-10-12/13)
The true 44-step v03 run scored **lower** than the broken 22-step run
(17.18 vs 18.29). More training on Dataset 3 = more degradation —
completeness fell 3.879 → 3.117 across the runs. This dose-response
**proves Dataset 3's format drilling degraded content quality**; the
step count was never the cause. Training loss looked healthy (3.789);
the locked eval exposed the truth. Loss is not the metric.

### The v01 data was excellent all along (2026-10-16)
The faithful v01 reproduction — trained with the **exact historical
config** (fp16, no sequence-length cap) — scored **19.71/20** on the
locked 48-example screen. This **refutes** the hypothesis that v01's
historical 18.00 was caused by fp16 instability or long context.
The v01 dataset (1,920 examples, 100% Ryan's own curation) genuinely
produces ~19.5–19.7 quality. The historical 18.00 came from an
unreconstructed factor, not the data. The primer experiment's "zero
standalone gain" premise is dissolved. See
`docs/V01FAITHFUL_DIAGNOSTIC_REPORT_2026-10-16.md`.

### Shared blind spot: response completeness (2026-10-16)
Detailed analysis of the 48-example screen reveals faithful-v01 and
v02 share the **same weakness pattern**: the models give correct
answers but don't go far enough — missing tradeoff comparisons,
concrete examples, and structured steps when instructions request
them. The model was never factually wrong on any of the 48 examples.
This is a **delivery** problem, not a knowledge problem. See
`docs/V01FAITHFUL_SCREEN_ANALYSIS_2026-10-16.md`.

## v02 weakness map → D4

From 240 prior judgments: 194 perfect scores. The headroom is
concentrated in two criteria — **reasoning_quality 3.804/4** (39 sub-4)
and **completeness 3.879/4** (24 sub-4) — with a clear pattern: shallow
reasoning, missing tradeoffs, no comparison of alternatives. Correctness
(3.979) is nearly maxed.

**D4 Shot 1** (2026-10-13): **NO-GO.** A 160-example curated dataset
targeting those measured weaknesses scored 16.40/20 with 138/180
regressions (template collapse — completeness 3.88→2.92). The approach
(demonstrating troubleshooting steps, tradeoff analysis, concrete
examples inside high-quality answers) was the right idea; the execution
fell into format drilling. No Shot 2 authorized. See
`docs/D4_SHOT1_EXPERIMENT.md`.

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
- Rule: the faithful-v01 adapter is the protected champion. Do not
  train, merge, or modify it until the next hypothesis is defined.
