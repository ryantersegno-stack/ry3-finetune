# v01 Primer Anomaly — Historical Reproduction Audit Report
**Date:** 2026-10-13 | **Investigator:** WR3N | **Status:** PRIMER EXPERIMENT REMAINS BLOCKED

## Executive Summary

The reproduced v01 scored 19.54/20 vs historical v01's 18.00/20 — a 1.54-point gap.
Audit of the historical training notebook (`ry3-github/staging/Untitled2.ipynb`)
recovered the actual v01 configuration. **Two material differences explain the gap:**
historical v01 used **fp16 mixed precision** (repro used fp32) and **SFTTrainer with
default max_seq_length** (~1024, repro used explicit 128). The historical 18.00 likely
reflects fp16 training instability, not a fundamental limit of the v01 data.

---

## A. Historical v01 Configuration

Recovered from `ry3-github/staging/Untitled2.ipynb` (cells 15, 17, 18, 19/20, 21).

| Parameter | Value | Status |
|---|---|---|
| Base model | saidutta69/Qwen3-1.7B-heretic | VERIFIED |
| Quantization | 4-bit NF4, double quant | VERIFIED |
| Compute dtype | torch.float16 | VERIFIED |
| Model dtype | torch.float16 | VERIFIED |
| LoRA r / alpha / dropout | 16 / 32 / 0.05 | VERIFIED |
| LoRA targets | q,k,v,o,gate,up,down (7) | VERIFIED |
| LoRA bias | none | VERIFIED |
| Epochs | 3 | VERIFIED |
| Per-device batch | 2 | VERIFIED |
| Gradient accumulation | 8 (eff batch 16) | VERIFIED |
| Learning rate | 1e-4 | VERIFIED |
| Optimizer | paged_adamw_8bit | VERIFIED |
| Gradient checkpointing | True | VERIFIED |
| **Precision** | **fp16=True** | **VERIFIED** |
| Trainer | SFTTrainer (TRL) | VERIFIED |
| Data formatting | Chat template via apply_chat_template | VERIFIED |
| Dataset | 1,920 examples (per v02 manifest) | VERIFIED |
| Warmup | warmup_ratio=0.05 (cell 19) OR warmup_steps=100 (cell 20) | VERIFIED (ambiguous which ran) |
| max_seq_length | NOT SET → TRL default | VERIFIED (not set) |
| Seed | NOT SET → random | VERIFIED (not set) |
| TRL version | — | UNKNOWN |
| Which cell ran (19 vs 20) | — | UNKNOWN |
| Final training loss | — | UNKNOWN |

---

## B. Current Reproduced v01 Configuration

From `eval_repair/primer_branchA_v01repro_train.py` (executed 2026-10-13).

| Parameter | Value | Status |
|---|---|---|
| Base model | saidutta69/Qwen3-1.7B-heretic | VERIFIED |
| Quantization | 4-bit NF4, double quant | VERIFIED |
| Compute dtype | torch.float16 | VERIFIED |
| LoRA r / alpha / dropout | 16 / 32 / 0.05 | VERIFIED |
| LoRA targets | q,k,v,o,gate,up,down (7) | VERIFIED |
| Epochs | 3 | VERIFIED |
| Per-device batch | 2, grad accum 8 (eff 16) | VERIFIED |
| Learning rate | 1e-4 | VERIFIED |
| Optimizer | paged_adamw_8bit | VERIFIED |
| Gradient checkpointing | True | VERIFIED |
| **Precision** | **fp32 (fp16=False, bf16=False)** | **VERIFIED** |
| **max_length** | **128 (explicit truncation)** | **VERIFIED** |
| **Seed** | **42** | **VERIFIED** |
| Warmup | warmup_steps=100 | VERIFIED |
| Trainer | Manual (HF Trainer, not SFTTrainer) | VERIFIED |
| Dataset | 1,920 RY3-ULTRA, SHA256 verified | VERIFIED |
| Final loss | 0.1067 | VERIFIED |

---

## C. Difference Matrix

| Variable | Historical v01 | Reproduced v01 | Material? |
|---|---|---|---|
| **Training precision** | fp16 | fp32 | **YES — HIGH** |
| **Max sequence length** | ~1024 (TRL default) | 128 (explicit) | **YES — HIGH** |
| **Seed** | Random (not set) | 42 | Likely not (1.5pt gap too large) |
| Warmup | 0.05 ratio OR 100 steps | 100 steps | Possibly (if cell 19 ran) |
| Trainer class | SFTTrainer | HF Trainer | Unlikely (functionally equivalent) |
| Data formatting | Chat template | Chat template | No |
| Dataset | 1,920 RY3-ULTRA | 1,920 RY3-ULTRA | No (verified clean) |

---

## D. Evaluation Audit

Per the forensics brief (`v01repro_anomaly_forensics.md`):
- Historical v01's 18.00 is real: 17.9958 on 240/240 (237 parsed).
- The 48-example screen uses `instructions[::5]` — fixed subset, fully comparable.
- Base on subset: 17.96 (screen) vs 18.03 (full) ✓
- v02 on subset: 19.62 (screen) vs 19.57 (full) ✓
- Historical v01 on the EXACT subset: **18.125** (computed from prior judgments).
- Reproduced v01 on subset: **19.54** — a genuine ~1.4-point outperformance.
- The 2 parse failures in the repro screen cannot explain the gap.
- **Verdict: 18.00 and 19.54 are genuinely comparable. The anomaly is real, not an eval artifact.**

---

## E. Data Audit

- Reproduced v01 dataset: 1,920 examples, all with RY3-ULTRA ID prefix, zero v02 examples. SHA256 `324610f73fe1afb7a2eff72811da23b8af587d13c48dfbf964db62f64393198b`.
- Historical v01 dataset: identified as `RY3_ULTRA_MASTER_DATASET_v01` (1,920 examples per v02 manifest).
- Both use chat-template formatting (instruction → user, output → assistant).
- **Verdict: Datasets are equivalent. Data contamination is ruled out.**

---

## F. Causal Hypothesis Ranking

### Hypothesis 1: fp16 vs fp32 training precision (Confidence: HIGH)
Historical v01 used `fp16=True`. fp16 mixed-precision training with LoRA on a 1.7B
model is susceptible to gradient underflow and unstable convergence, especially with
a high learning rate (1e-4). The reproduced v01 used fp32, which is more stable and
likely converged to a better optimum. The 1.5-point gap is consistent with precision-
induced undertraining in the historical run.

**Evidence:** Direct config difference, VERIFIED from both the historical notebook
(cell 19/20: `fp16=True`) and the reproduction script (`fp16=False, bf16=False`).
fp16 instability with LoRA is a well-documented phenomenon.

### Hypothesis 2: max_length 1024 vs 128 (Confidence: MEDIUM-HIGH)
Historical v01 used SFTTrainer default max_seq_length (~1024). The reproduction
truncated to 128. With 128, the model sees only short, focused examples — this acts
as an implicit regularizer and forces the model to learn concise, high-signal patterns.
With 1024, the model may have overfit to longer, noisier sequences or suffered from
attention dilution.

**Evidence:** Direct config difference. Historical notebook does not set max_seq_length;
repro sets 128 explicitly. The 128 cap may have inadvertently improved generalization.

### Hypothesis 3: Warmup configuration (Confidence: LOW-MEDIUM)
If historical v01 ran cell 19 (warmup_ratio=0.05 = ~18 steps) instead of cell 20
(warmup_steps=100), the shorter warmup with lr 1e-4 could have caused early instability.
But this alone is unlikely to explain 1.5 points.

**Evidence:** Ambiguity in historical records (two cells exist). Cannot determine which ran.

### Hypothesis 4: Seed variation (Confidence: LOW)
Random seed vs 42. Seed can cause ~0.1-0.3 point variation, not 1.5 points.

### Hypothesis 5: Evaluation artifact (Confidence: RULED OUT)
The forensics brief definitively ruled this out. The numbers are comparable.

---

## G. Recommended Minimal Experiment

To discriminate between Hypothesis 1 (precision) and Hypothesis 2 (max_length):

**Experiment:** Train v01-faithful reproduction with:
- fp16=True (matching historical)
- SFTTrainer with default max_seq_length (matching historical)
- All other settings identical to current repro (seed 42, warmup 100, etc.)
- Evaluate on the same 48-example screen

**Decision logic:**
- If faithful repro ≈ 18.00 → Hypothesis 1 and/or 2 confirmed. The historical 18.00 was a config artifact.
- If faithful repro ≈ 19.54 → The gap is NOT from precision/max_length. Investigate further (warmup? TRL version?).
- To isolate further: run fp16+128 and fp32+1024 as a 2x2 ablation (only if the first test is inconclusive).

**Estimated cost:** ~25 min L4 (~4 compute units). Minimal and decisive.

**DO NOT run this until Ryan approves.** The directive says to produce the hypothesis ranking first.

---

## H. Primer Experiment Status

**REMAINS BLOCKED.**

The primer experiment cannot resume until the 19.54 anomaly is explained. The current
evidence strongly suggests the historical v01's 18.00 was a training-config artifact
(fp16 + long context), not a fundamental property of the v01 data. If confirmed, the
"zero standalone gain" premise of the primer experiment dissolves — the v01 data was
always capable of producing v02-level performance; the historical run simply didn't.

Branch A Stage 2, Branch B, and the full eval remain frozen. No additional compute
will be burned without Ryan's explicit approval. The 19.54 adapter
(`RY3_PRIMER_A_v01repro`) is preserved as an experimental artifact. Historical v02
champion untouched.

---

## Artifact Preservation

The following are preserved and must not be modified:
- Adapter: `/content/drive/MyDrive/RY3/RY3_PRIMER_A_v01repro/`
- Training report: `PRIMER_A_V01REPRO_TRAINING_REPORT.json` (in adapter dir)
- Dataset: `eval_repair/dataset_v01_1920.jsonl` (SHA256 verified)
- Eval script: `eval_repair/primer_v01repro_screen_eval.py`
- Forensics brief: `eval_repair/v01repro_anomaly_forensics.md`
- This report: `eval_repair/v01_historical_audit_report.md`
- Historical notebook: `ry3-github/staging/Untitled2.ipynb` (source of v01 config)
