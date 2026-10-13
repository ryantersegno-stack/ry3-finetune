# WR3N HANDOFF: RY3 QWEN3 TRAINING PROJECT

**Prepared for WR3N, the Muse agent helping run the next Colab training/evaluation cycle.**

---

## 0. Executive summary

The project is a Qwen3-1.7B Heretic LoRA training lineage:

```text
Qwen3-1.7B-heretic
        |
        v
     RY3 v01
  1,920 examples
        |
        v
     RY3 v02
  2,720 cumulative
  (1,920 + 800)
```

The authoritative base model is:

`saidutta69/Qwen3-1.7B-heretic`

The notebook's references to `Qwen2.5-3B` appear to be stale material and should not be treated as the actual RY3 base unless the original notebook proves otherwise.

The biggest current problem is **evaluation, not necessarily training**. v02 produced 240 eval responses, but the judge stage returned outputs that were ordinary answers rather than the required JSON grading objects. The parser consequently converted all 240 judgments into zeros. **Those zeros are not valid evidence that v02 performed poorly.**

The immediate priority should therefore be to repair/re-run evaluation on the locked 240-example set before doing another training run.

---

# 1. Base model

### Confirmed base

`saidutta69/Qwen3-1.7B-heretic`

This is **Qwen3 1.7B Heretic**, not Qwen2.5-3B.

The intended lineage is:

```text
Base Qwen3-1.7B-heretic
        ↓
RY3_QWEN3_1.7B_v01
        ↓
RY3_QWEN3_1.7B_v02
```

If `Qwen2.5-3B` appears in a notebook cell, config, or comment, treat it as legacy/stale material until verified against the actual run artifacts.

---

# 2. Training configuration

## RY3 v01

| Setting | Value |
|---|---|
| Base model | `saidutta69/Qwen3-1.7B-heretic` |
| LoRA rank (`r`) | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Learning rate | `1e-4` |
| Epochs | 3 |
| Per-device batch size | 2 |
| Gradient accumulation | 8 |
| Effective batch size | 16 |
| Optimizer | `paged_adamw_8bit` |
| Adapter name | `RY3_QWEN3_1.7B_v01` |

### v01 adapter

```text
/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v01
```

---

## RY3 v02

v02 was a **continuation of v01**, not an independent fresh training run.

| Setting | Value |
|---|---|
| Base/model lineage | Qwen3-1.7B-heretic → v01 → v02 |
| Starting point | v01 adapter |
| LoRA rank (`r`) | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Learning rate | `5e-5` |
| Epochs | 2 |
| Per-device batch size | 2 |
| Gradient accumulation | 8 |
| Effective batch size | 16 |
| Optimizer | `paged_adamw_8bit` |
| Training examples | 2,720 |
| Reported steps | 340 |
| Reported final loss | 0.42649 |
| Adapter name | `RY3_QWEN3_1.7B_v02` |

### v02 adapter

```text
/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v02
```

### Important unknown

The exact `max_length` value was not reliably preserved in the session records.

**Do not guess it.** Inspect the original Colab training cell/config and record the actual value before the next run.

---

# 3. What "training one" and "training two" mean

## Training 1 = RY3 v01

Started from:

`saidutta69/Qwen3-1.7B-heretic`

Training set:

**1,920 examples**

Produced:

`RY3_QWEN3_1.7B_v01`

---

## Training 2 = RY3 v02

Continuation from:

**RY3 v01**

Training corpus:

**1,920 original + 800 new = 2,720 cumulative examples**

Produced:

`RY3_QWEN3_1.7B_v02`

No other completed RY3 training run is confirmed in the recovered project records.

---

# 4. Dataset 1

## Original training dataset

**1,920 examples**

Recorded location:

```text
/content/drive/MyDrive/RY3/RY3_ULTRA_MASTER_DATASET_v01
```

The master dataset structure included:

- TRAIN
- EVAL
- FULL
- manifest
- hashes

The training records are JSONL-style structured instruction/response data.

Known fields include:

```text
id
instruction
output
category
skill
difficulty
source
quality_profile
```

Example record IDs seen in the project include:

```text
88fsw3
```

The dataset is the RY3 instruction/response training corpus organized by category, skill, difficulty, source, and quality profile.

---

# 5. Dataset 2

## 800 new examples

The second data addition contained:

**800 new examples**

The cumulative v02 training dataset was:

**2,720 examples total**

```text
1,920 original
+
800 new
=
2,720 cumulative
```

Recorded cumulative file:

```text
/content/drive/MyDrive/RY3/RY3_CUMULATIVE_V02_TRAIN.jsonl
```

Known fields:

```text
id
instruction
output
category
skill
difficulty
source
quality_profile
```

Example record ID seen in the project:

```text
3u39ls
```

---

# 6. Dataset 3

A finalized Dataset 3 specification was not preserved in the recovered project records.

Therefore:

**Do not assume a Dataset 3 exists or invent its composition.**

The current known training state ends at:

**v02 = 2,720 cumulative training examples.**

Dataset 3 should be deliberately designed and documented before the next training run.

---

# 7. Locked 240-example evaluation set

The project has a **locked 240-example evaluation benchmark**.

Recorded location:

```text
/content/drive/MyDrive/RY3/RY3_ULTRA_MASTER_DATASET_v01/RY3_ULTRA_MASTER_DATASET_v01_EVAL.jsonl
```

Format:

**JSONL**

Known fields:

```text
id
instruction
output
category
skill
difficulty
source
quality_profile
```

Example ID seen:

```text
b1yxt8
```

### Evaluation rule

The 240 examples should remain locked.

Use the **same 240 prompts** for Base, v01, and v02 so comparisons remain valid.

Do not add training examples to this evaluation set.

---

# 8. Judge model and scoring

The intended judge was the **clean base Qwen3 model**, rather than the Heretic-trained adapter.

The judge was expected to return **ONLY JSON**.

The scoring dimensions were:

```text
correctness
relevance
completeness
instruction_following
reasoning_quality
```

Each was scored on a **0–4** scale.

The response was also expected to include:

```text
brief_reason
```

Expected conceptual format:

```json
{
  "correctness": 0,
  "relevance": 0,
  "completeness": 0,
  "instruction_following": 0,
  "reasoning_quality": 0,
  "brief_reason": "..."
}
```

The exact judge prompt should be recovered from the original evaluation notebook if possible. Do not silently rewrite the historical prompt if the goal is to reproduce prior results.

---

# 9. v01 evaluation artifacts

v01 has usable evaluation artifacts.

Recorded location:

```text
/content/drive/MyDrive/RY3/RY3_EVAL_v01/
```

Known files:

```text
base_results.jsonl
ry3_results.jsonl
base_judgments.jsonl
ry3_judgments.jsonl
```

There were 240 responses for each side.

Recorded v01 comparison:

```text
RY3 wins: 18
Base wins: 16
Ties: 206
```

Recorded average judge advantage:

```text
approximately +0.138 / 20
```

Additional v01 response statistics:

| Metric | Value |
|---|---:|
| Eval responses | 240 |
| Average response length | 272.9875 characters |
| Very-short responses | 0 |
| Repetition signal | 12 |
| Longest response | 418 characters |

These results are useful as a historical baseline, but the exact original judge implementation should be preserved/recovered if the experiment is being reproduced.

---

# 10. v02 evaluation failure

This is the most important debugging issue.

v02 generated:

**240 evaluation responses**

However, the judge stage produced:

**240 / 240 parse errors**

The resulting judgments were effectively all zeros.

Recorded judgment file:

```text
/content/drive/MyDrive/RY3/RY3_EVAL_v02/ry3_v02_judgments.jsonl
```

### Critical interpretation

The zeros **do NOT mean v02 scored zero on the benchmark.**

The judge failed to produce the required JSON.

Instead of returning something like:

```json
{
  "correctness": 3,
  "relevance": 4,
  "completeness": 3,
  "instruction_following": 4,
  "reasoning_quality": 3,
  "brief_reason": "..."
}
```

the judge was returning ordinary natural-language answers to the underlying evaluation questions.

The parser expected the structured grading object.

Therefore:

```text
judge outputs ordinary answer
        ↓
JSON parser fails
        ↓
parse error
        ↓
fallback/forced zero
```

This is an **evaluation pipeline failure**, not a demonstrated model-quality failure.

---

# 11. Artifact locations

## v01 adapter

```text
/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v01
```

## v02 adapter

```text
/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v02
```

## Master dataset

```text
/content/drive/MyDrive/RY3/RY3_ULTRA_MASTER_DATASET_v01
```

## Cumulative v02 training dataset

```text
/content/drive/MyDrive/RY3/RY3_CUMULATIVE_V02_TRAIN.jsonl
```

## Locked eval

```text
/content/drive/MyDrive/RY3/RY3_ULTRA_MASTER_DATASET_v01/RY3_ULTRA_MASTER_DATASET_v01_EVAL.jsonl
```

## v01 evaluation directory

```text
/content/drive/MyDrive/RY3/RY3_EVAL_v01/
```

## v02 judgments

```text
/content/drive/MyDrive/RY3/RY3_EVAL_v02/ry3_v02_judgments.jsonl
```

---

# 12. Recommended next-run procedure

Before training anything new:

## Step 1: Verify the actual artifacts

Confirm that these exist:

```text
RY3_QWEN3_1.7B_v01
RY3_QWEN3_1.7B_v02
RY3_CUMULATIVE_V02_TRAIN.jsonl
RY3_ULTRA_MASTER_DATASET_v01_EVAL.jsonl
```

Also inspect the original Colab notebook/config for:

- exact `max_length`
- tokenizer configuration
- data formatting function
- LoRA configuration
- training arguments
- exact judge prompt
- exact parser implementation

---

## Step 2: Re-run the locked evaluation

Run the **same 240 locked evaluation examples** against:

1. Base Qwen3-1.7B-heretic
2. RY3 v01
3. RY3 v02

Save the raw generated responses before judging.

Suggested structure:

```text
RY3_EVAL_REPAIR/
    base_results.jsonl
    v01_results.jsonl
    v02_results.jsonl
```

---

## Step 3: Test the judge on a small sample FIRST

Do not launch another 240-example judge run immediately.

Run perhaps 5–10 examples and inspect the raw judge outputs.

Require:

```text
valid JSON
correct field names
integer scores
scores within 0–4
brief_reason present
```

If even one output is malformed, diagnose the judge generation/parsing pipeline before processing all 240.

---

## Step 4: Make parsing robust

The evaluator should:

1. Capture raw judge output.
2. Attempt strict JSON parsing.
3. Validate the required keys.
4. Validate score ranges.
5. Record malformed output separately.
6. Never silently convert a parser failure into a legitimate model score of zero.

Recommended record structure:

```json
{
  "eval_id": "...",
  "raw_judge_output": "...",
  "parsed": true,
  "correctness": 3,
  "relevance": 4,
  "completeness": 3,
  "instruction_following": 4,
  "reasoning_quality": 3,
  "brief_reason": "..."
}
```

For malformed outputs:

```json
{
  "eval_id": "...",
  "raw_judge_output": "...",
  "parsed": false,
  "parse_error": "..."
}
```

That distinction prevents an evaluator bug from masquerading as model failure.

---

# 13. Experimental comparison to preserve

The key scientific question is:

> **Did v02 actually improve over v01 after adding 800 examples and continuing training at a lower learning rate?**

We currently cannot answer that from the existing v02 judge scores because those scores are contaminated by the judge/parser failure.

The correct experiment is therefore:

```text
             SAME 240 LOCKED EVAL
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
     BASE           v01           v02
       |             |             |
       +-------------+-------------+
                     |
                     v
              SAME FIXED JUDGE
                     |
                     v
              VALIDATED JSON
                     |
                     v
             COMPARATIVE SCORES
```

---

# 14. What WR3N should NOT assume

Do not assume:

- Qwen2.5-3B was the actual base model.
- v02's all-zero scores mean v02 failed.
- v02 was trained only on the 800 new examples.
- Dataset 3 already exists.
- `max_length` from memory.
- The old judge prompt is correct without checking the notebook.
- A parser error is equivalent to a score of zero.
- A new training run is necessary before repairing evaluation.

---

# 15. One-page state summary

### MODEL

```text
saidutta69/Qwen3-1.7B-heretic
```

### LINEAGE

```text
Qwen3-1.7B-heretic
        ↓
v01
        ↓
v02
```

### DATA

```text
v01: 1,920 examples
v02: 2,720 cumulative examples
     = 1,920 + 800
eval: 240 locked examples
```

### LoRA

```text
r = 16
alpha = 32
dropout = 0.05

targets:
q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

### TRAINING

```text
v01:
LR 1e-4
3 epochs
effective batch 16

v02:
LR 5e-5
2 epochs
effective batch 16
```

### ARTIFACTS

```text
Drive:
 /MyDrive/RY3/RY3_QWEN3_1.7B_v01
 /MyDrive/RY3/RY3_QWEN3_1.7B_v02
 /MyDrive/RY3/RY3_ULTRA_MASTER_DATASET_v01
 /MyDrive/RY3/RY3_CUMULATIVE_V02_TRAIN.jsonl
```

### EVAL STATUS

```text
v01: usable historical evaluation artifacts
v02: 240 responses exist
v02 judge: BROKEN
v02 scores: INVALID / DO NOT INTERPRET AS MODEL QUALITY
```

### NEXT MOVE

```text
REPAIR EVALUATION FIRST.
THEN compare Base vs v01 vs v02.
THEN decide whether Dataset 3 / Training 3 is warranted.
```

---

# 16. Final instruction to WR3N

Take the wheel from here, but preserve the experiment's lineage.

**First recover the original Colab notebook/config and verify every uncertain parameter. Then repair the evaluation pipeline and re-score the existing v01/v02 artifacts against the locked 240-example benchmark. Do not launch another training run merely to compensate for a broken evaluator.**

The project already has enough trained material to answer the most important question first:

**Did the additional 800 examples and v02 continuation actually make RY3 better?**

Once that is established, design the next training run from evidence rather than guesswork.
