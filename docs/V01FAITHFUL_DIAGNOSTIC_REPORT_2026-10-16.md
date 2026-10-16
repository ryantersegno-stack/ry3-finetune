# RY3 Faithful-v01 Diagnostic — Full Report
**Date:** 2026-10-16
**Author:** WR3N (for Ryan / KING_RY3)
**Purpose:** Complete record of the faithful v01 reproduction diagnostic for Mira's database/memory

---

## 1. Background: Why This Diagnostic Exists

### The RY3 Campaign (Summary)
Ryan fine-tunes Qwen3-1.7B. His champion adapter **v02** scores **19.57/20** on a locked 720-judgment eval (240 examples × 3 runs). Every continuation from v02 has failed its gates. v02 stays untouched.

### The Primer Theory Experiment
Hypothesis: v01 acted as a "latent primer" — its data did nothing on its own (~18.00 standalone) but unlocked v02's gains when used as a stepping stone.

- **Branch A:** BASE → reproduced v01 → v02
- **Branch B:** BASE → v02 direct

### The Anomaly (2026-10-13)
Branch A Stage 1 (reproduced v01) scored **19.54/20** instead of the expected ~18.00. This triggered the experiment's STOP condition — the "zero standalone gain" premise was violated. Experiment FROZEN.

### The Suspect: Training Config
Historical audit recovered the original v01 config: **fp16=True** and **SFTTrainer with default max_seq_length** (~131072, effectively uncapped). My reproduction used fp32 + max_length=128. Leading hypothesis: the original 18.00 was a training-config artifact (fp16 instability + long context), not a fundamental limit of the v01 data.

### The Diagnostic Directive
Ryan approved a single faithful reproduction: train v01 EXACTLY as the original (fp16, no seq-length cap), then run the locked 48-example screen.
- **~18.0** → implicates the historical fp16/sequence config (theory confirmed)
- **~19.5** → refutes it; the 19.54 reproduction was valid (theory dead)

---

## 2. Training Configuration (Faithful)

| Parameter | Value |
|---|---|
| Base model | saidutta69/Qwen3-1.7B-heretic (4-bit NF4 double-quant) |
| Dataset | v01, 1,920 examples (SHA256: 324610f7...b — verified) |
| Trainer | trl.SFTTrainer |
| max_seq_length | NOT set (resolved to 131072 — faithful to original) |
| Precision | fp16=True, bf16=False (faithful to original) |
| Learning rate | 1e-4 |
| Epochs | 3 |
| Effective batch | 16 (per_device=2, grad_accum=8) |
| Optimizer | paged_adamw_8bit |
| Gradient checkpointing | True |
| LoRA | r=16, alpha=32, dropout=0.05; targets: q/k/v/o/gate/up/down_proj |
| Warmup steps | 100 |
| Seed | 42 |
| Total steps | 360 (1920 ÷ 16 = 120/epoch × 3 epochs) |
| Checkpointing | Every 40 steps, 3 kept, saved to Drive |
| GPU | L4 (52.96 GB RAM) |
| Output dir | Drive: RY3/RY3_PRIMER_V01FAITHFUL |

### Training Result
- **Steps completed:** 360/360
- **Final loss:** 0.9819 (down from ~6.0 at step 83 of the earlier interrupted attempt)
- **Runtime:** 2046.7s (~34.1 min), 2.814 samples/sec
- **Epochs:** 3.0/3.0 — full completion
- **Checkpoints:** checkpoint-200, checkpoint-360 + final adapter all in Drive
- **Report:** V01FAITHFUL_TRAINING_REPORT.json in output dir

Note: An earlier attempt (Oct 13–15) reached 83/360 before Colab disconnects killed it. The run completed overnight 2026-10-16 when Ryan's phone L4 session continued in the background.

---

## 3. Evaluation: 48-Example Locked Screen

### Protocol
- 48 examples (every 5th of the locked 240)
- Candidate generation: max_new 200, temp 0.7, top_p 0.8, top_k 20
- Judge: Qwen3-1.7B bf16, temp 0.1, verbatim judge prompt + strict parser
- Compared against base and v02 PRIOR judgments on the SAME 48 examples
- 0 parse failures

### Results

| Model | Mean (/20) |
|---|---|
| **Faithful v01** | **19.71** |
| v02 (priors) | 19.62 |
| Base (priors) | 17.96 |

### Per-Criterion (/4)

| Criterion | Base | v02 | Faithful v01 |
|---|---|---|---|
| Correctness | 3.646 | 4.000 | 3.979 |
| Relevance | 3.667 | 3.958 | 4.000 |
| Completeness | 3.396 | 3.917 | 3.917 |
| Instruction following | 3.812 | 3.938 | 3.979 |
| Reasoning quality | 3.438 | 3.812 | 3.833 |

### Regressions (screening subset)
- vs base: 2/48
- vs v02: 5/48

### Delta
- +0.08 vs v02's full-eval 19.57 on the screening subset
- (Screening subset means are NOT directly comparable to full-240 eval means)

### Output Files (Drive: RY3/eval_primer_v01faithful/)
- v01faithful_screen_judgments.jsonl (33,597 bytes)
- v01faithful_screen_results.jsonl (39,202 bytes)
- v01faithful_screen_scoreboard.txt (1,083 bytes)

---

## 4. Diagnostic Verdict: THEORY REFUTED

**The faithful v01 reproduction scored 19.71/20 — decisively in the ~19.5 range, not ~18.0.**

The hypothesis that the original v01's ~18.00 was caused by fp16 instability or uncapped sequence length is **refuted**. We reproduced those exact settings and got 19.71.

### What This Means
1. **The v01 data is genuinely excellent.** It produces ~19.5–19.7 standalone, regardless of fp16 vs fp32 or sequence-length capping.
2. **The historical 18.00 came from something else.** Possible causes: a different dataset version, different code, different eval setup, or another undocumented factor. The historical audit could not fully reconstruct the original run environment.
3. **The primer experiment's "zero standalone gain" premise is dissolved.** v01 was never a ~18.00 dataset. The Branch A Stage 1 result (19.54) was not an anomaly — it was accurate.
4. **v02's gains are smaller than assumed.** If v01 alone reaches ~19.7, then v02's 19.57 represents refinement, not a breakthrough from a weak foundation.

### What This Does NOT Mean
