# RY3 v02 Deep Analysis & Dataset 3 Specification
*2026-10-12. Analysis of the repaired 720-judgment eval (240 eval IDs × base/v01/v02). No training performed. Locked eval set untouched.*

---

## 1. Headline results (measured)

| Model | n parsed | Parse rate | Mean /20 |
|---|---|---|---|
| base (saidutta69/Qwen3-1.7B-heretic) | 240/240 | 100.0% | 18.03 |
| RY3 v01 | 237/240 | 98.8% | 18.00 |
| RY3 v02 | 240/240 | 100.0% | 19.57 |

- v02 vs base: **+8.5%**. v02 vs v01: **+8.7%**. v01 vs base: **-0.2%** (a wash).
- v02 scored a perfect 20/20 on **194/240** evals (81%); base did so on 89/240 (37%).
- v01's 3 parse failures (excluded from its mean, not zeroed): RY3-ULTRA-00506, RY3-ULTRA-00863, RY3-ULTRA-01688.

## 2. Per-criterion breakdown — what drove the gain (measured)

| Criterion | base | v01 | v02 | v02−base |
|---|---|---|---|---|
| correctness | 3.721 | 3.722 | 3.979 | **+0.258** |
| relevance | 3.700 | 3.671 | 3.954 | **+0.254** |
| completeness | 3.333 | 3.262 | 3.879 | **+0.546** |
| instruction_following | 3.788 | 3.827 | 3.954 | **+0.167** |
| reasoning_quality | 3.492 | 3.515 | 3.804 | **+0.312** |

**Completeness (+0.546) is the dominant driver** — more than double any other criterion. Base's weakest axis was completeness (3.333); v02 fixed it. v01 moved nothing (all deltas vs base within ±0.07).

## 3. Category analysis (measured)

The eval instructions carry explicit format constraints, yielding 5 natural categories:

| Category | n | base | v01 | v02 | v02−base | win/tie/loss (v02 vs base) |
|---|---|---|---|---|---|---|
| compare_tradeoff ("Compare the main alternatives and state the tradeoff") | 52 | 17.29 | 17.73 | 19.44 | **+2.15** | 31/17/4 |
| other ("Explain the answer and the reasoning…") | 42 | 18.12 | 17.90 | 19.81 | **+1.69** | 25/15/2 |
| concise_keychecks ("Give a concise answer followed by the key checks") | 57 | 18.30 | 18.00 | 19.82 | **+1.53** | 34/20/3 |
| explain_example ("Explain the main idea, then give one concrete example") | 40 | 18.23 | 18.08 | 19.38 | **+1.15** | 19/17/4 |
| troubleshoot_steps ("Answer as a troubleshooting guide with ordered steps") | 49 | 18.29 | 18.29 | 19.37 | **+1.08** | 26/17/6 |

Per-criterion deltas within categories (v02 − base):

| Category | correctness | relevance | completeness | instr_following | reasoning |
|---|---|---|---|---|---|
| compare_tradeoff | +0.423 | +0.404 | +0.615 | +0.308 | +0.404 |
| concise_keychecks | +0.263 | +0.211 | +0.614 | **+0.070** | +0.368 |
| explain_example | +0.200 | +0.250 | +0.375 | +0.225 | +0.100 |
| other | +0.286 | +0.310 | +0.595 | +0.167 | +0.333 |
| troubleshoot_steps | +0.102 | +0.102 | +0.490 | **+0.082** | +0.306 |

**Key finding:** on the two most format-rigid categories (troubleshoot_steps, concise_keychecks), v02's instruction_following barely moved (+0.07–0.08) even as completeness surged. v02 writes fuller, more correct answers but is **no more obedient to structural format requirements than base** — and sometimes less (see regressions).

Per-audience deltas (v02 − base): beginner **+2.36** (n=28), engineer +2.03 (36), reviewer +1.71 (38), analyst +1.39 (49), practitioner +1.31 (48), student +0.83 (41). v02 is notably better at beginner-accessible explanations. (Audience n's are small; treat as suggestive, not conclusive.)

## 4. Top 15 gains — v02 over base (measured)

| Δ | Eval ID | base→v02 | Category |
|---|---|---|---|
| +8 | RY3-ULTRA-00657 | 12→20 | compare_tradeoff |
| +8 | RY3-ULTRA-00265 | 11→20 | compare_tradeoff |
| +7 | RY3-ULTRA-01885 | 13→20 | compare_tradeoff |
| +7 | RY3-ULTRA-00913 | 13→20 | troubleshoot_steps |
| +6 | RY3-ULTRA-01889 | 14→20 | compare_tradeoff |
| +6 | RY3-ULTRA-01566 | 14→20 | other |
| +6 | RY3-ULTRA-00994 | 13→19 | explain_example |
| +6 | RY3-ULTRA-00855 | 14→20 | compare_tradeoff |
| +6 | RY3-ULTRA-00504 | 14→20 | concise_keychecks |
| +6 | RY3-ULTRA-00369 | 14→20 | concise_keychecks |
| +6 | RY3-ULTRA-00355 | 14→20 | concise_keychecks |
| +6 | RY3-ULTRA-00024 | 14→20 | concise_keychecks |
| +5 | RY3-ULTRA-02128 | 15→20 | concise_keychecks |
| +5 | RY3-ULTRA-02048 | 15→20 | concise_keychecks |
| +5 | RY3-ULTRA-02018 | 15→20 | concise_keychecks |

Pattern (inference): the biggest gains are where base gave thin, under-developed answers (11–15/20) and v02 delivered the full, well-structured treatment. v02's completeness training paid off most where base was weakest.

## 5. All 19 regressions — v02 below base (measured)

| Δ | Eval ID | base/v01/v02 | Category | Failure mode (from judge brief_reason) |
|---|---|---|---|---|
| −4 | RY3-ULTRA-01583 | 20/18/16 | explain_example | Example **identical to reference** — parroted instead of generating a fresh example |
| −4 | RY3-ULTRA-01814 | 18/20/14 | troubleshoot_steps | **No ordered steps** despite explicit format request |
| −3 | RY3-ULTRA-00791 | 20/19/17 | concise_keychecks | **Key checks omitted** |
| −3 | RY3-ULTRA-00793 | 14/14/11 | troubleshoot_steps | No actionable ordered steps |
| −3 | RY3-ULTRA-01288 | 19/16/16 | compare_tradeoff | **No comparison of alternatives / no tradeoff stated** |
| −3 | RY3-ULTRA-01514 | 19/19/16 | troubleshoot_steps | No ordered steps |
| −2 | RY3-ULTRA-00050 | 20/20/18 | concise_keychecks | Key checks omitted |
| −2 | RY3-ULTRA-00329 | 20/18/18 | concise_keychecks | (format thinning) |
| −2 | RY3-ULTRA-00912 | 20/20/18 | concise_keychecks | Key checks omitted |
| −2 | RY3-ULTRA-00980 | 18/18/16 | explain_example | **No concrete example given** |
| −2 | RY3-ULTRA-01454 | 18/18/16 | troubleshoot_steps | No steps |
| −2 | RY3-ULTRA-01775 | 20/20/18 | concise_keychecks | Key checks omitted |
| −2 | RY3-ULTRA-02116 | 20/12/18 | troubleshoot_steps | (v01 was worse at 12; v02 recovered partially) |
| −1 | RY3-ULTRA-00487 | 19/18/18 | concise_keychecks | Key checks omitted |
| −1 | RY3-ULTRA-00506 | 20/FAIL/19 | explain_example | — |
| −1 | RY3-ULTRA-00690 | 15/15/14 | compare_tradeoff | No comparison/tradeoff |
| −1 | RY3-ULTRA-01404 | 20/20/19 | explain_example | — |
| −1 | RY3-ULTRA-01776 | 20/15/19 | concise_keychecks | — |
| −1 | RY3-ULTRA-02117 | 20/20/19 | concise_keychecks | — |

**The regression pattern is structural, not topical:** 15 of 19 regressions are v02 dropping an explicitly required structural element — ordered steps (6), key checks (6), comparison+tradeoff (2), concrete example (1). The remaining notable case (01583) is v02 **parroting the reference answer's example** instead of generating its own.

## 6. Root cause — the training data never taught format obedience (measured)

Checked all 2,720 training examples in `RY3_CUMULATIVE_V02_TRAIN.jsonl` for whether outputs honor their instructions' format constraints:

| Instruction format | Examples | Outputs honoring the format |
|---|---|---|
| "troubleshooting guide with ordered steps" | 383 | **0** (no ordered steps in any output) |
| "concise answer followed by the key checks" | 375 | **0** (no key checks mentioned) |
| "compare the main alternatives and state the tradeoff" | 380 | **13** (3.4%) |
| "explain the main idea, then give one concrete example" | 392 | **26** (6.6%) |

**The model was trained on 2,720 examples whose outputs systematically ignore structural format constraints.** v02's format disobedience isn't a mystery — it's exactly what the data taught. Content quality (completeness, correctness) improved because the outputs are substantively good; format discipline didn't because the outputs never modeled it.

Secondary observation: the 01583 parroting case suggests some training outputs hew too close to reference phrasing. The quality rules already say "avoid repetitive templates and shallow paraphrases" (rule 15) — this needs a sharper "generate fresh examples, never copy the reference" rule.

---

## 7. Hyperparameter record — v01/v02 reproduction (from staging artifacts)

### v01 (Untitled2.ipynb, cells 19–30; final run cell 30)

| Parameter | Value | Source |
|---|---|---|
| Base model | saidutta69/Qwen3-1.7B-heretic, loaded 4-bit NF4 (bnb_config, double quant, fp16 compute) | cell 15/27 |
| Method | LoRA via TRL SFTTrainer + peft_config | cell 29 |
| Dataset | 1,920 examples, chat-templated text (no pre-tokenization in code path used) | manifest + cell 17 |
| Epochs | 3 | cell 23 (final args) |
| Learning rate | 1e-4 | cell 23 |
| Per-device batch | 2 | cell 23 |
| Gradient accumulation | 8 (effective batch 16) | cell 23 |
| Warmup | warmup_steps=100 (cell 19 had warmup_ratio=0.05; superseded) | cell 23 |
| Optimizer | paged_adamw_8bit | cell 23 |
| Precision | fp16=False, bf16=False (fp32; cell 19/20 had fp16=True, superseded) | cell 23 |
| Gradient checkpointing | True | cell 23 |
| LR scheduler | linear (default; not explicitly set) | default |
| Seed | not set (transformers default 42 applies) | — |
| max_seq_length | **not explicitly set** — SFTTrainer default applies (TRL default 1024; version not recorded) | — |
| LoRA | r=16, alpha=32, dropout=0.05, bias none, targets q/k/v/o + gate/up/down | cell 18, adapter_config.json |
| Result | 360 steps, final loss 1.00837 | cell 30 output |

### v02 (Untitled2.ipynb, cells 60–76; final run cell 76)

| Parameter | Value | Source |
|---|---|---|
| Starting point | **v01 adapter loaded onto base with is_trainable=True** (genuine continuation, not fresh) | cell 61 |
| Method | plain transformers `Trainer` (not SFTTrainer) + DataCollatorForLanguageModeling (mlm=False) | cell 75 |
| Dataset | cumulative 2,720 (1,920 v01 + 800 new), pre-tokenized | cell 74–76 |
| Tokenization | truncation=True, **max_length=2048** (code ground truth) | cell 74 |
| Epochs | 2 | cell 72 |
| Learning rate | 5e-5 | cell 72 |
| Per-device batch | 2 | cell 72 |
| Gradient accumulation | 8 (effective batch 16) | cell 72 |
| Warmup | warmup_steps=100 | cell 72 |
| Optimizer | paged_adamw_8bit | cell 72 |
| Precision | fp16=False, bf16=False (fp32) | cell 72 |
| Gradient checkpointing | True | cell 72 |
| LR scheduler | linear (default; not explicitly set) | default |
| Seed | not set (transformers default 42 applies) | — |
| LoRA | same as v01 (continued adapter): r=16, alpha=32, dropout=0.05 | cell 60/61 |
| Result | 340 steps, final loss 0.42649, 1353.6s runtime | cell 76 output |
| peft version | 0.21.1 | adapter_config.json |

### ⚠️ max_length discrepancy (flagged, unresolved)

- **Code ground truth (cell 74):** `tokenizer(example["text"], truncation=True, max_length=2048)`.
- **Manifest claim:** `"max_length": 128` (RY3_v02_MANIFEST.json + staging copy).
- **Data reality:** training examples are short (mean ~64 est. tokens, max ~99 + chat-template overhead ≈ 100–150 tokens). At 128, a small number of the longest examples would truncate; at 2048, nothing truncates.
- **Verdict:** the manifest's 128 is **not supported by the training code**. Most likely an authoring error in the manifest (possibly confused with the token-length analysis in cells 78–79, which examined utilization at 128). For reproduction, use **2048** (what the code did). The practical difference is negligible given the data length distribution, but the record should reflect the code, not the manifest.

### Cannot be determined (do not guess)
- Exact TRL version used for v01's SFTTrainer (affects the default max_seq_length).
- Random seed (never set; framework default assumed but not verified in the run environment).
- Which base-model instance cell 61's `base_model` referred to at execution time (cell 41's fp16 unquantized load is the most recent assignment before it; v01's adapter was trained against a 4-bit base — a minor base/adapter precision mismatch worth noting, unlikely to matter for LoRA math but recorded here).
- v01's effective max_seq_length (framework default; see above).

---

## 8. Dataset 3 specification — format-obedience training

**Objective:** teach v02's successor to honor explicit structural format constraints without losing the completeness/correctness gains.

**What to build:** 300–400 new instruction→output pairs with these properties:

1. **Format-exemplifying outputs (the core fix, ~70% of Dataset 3):**
   - "Troubleshooting guide with ordered steps" → outputs that ACTUALLY contain numbered ordered steps (1. 2. 3.), each a concrete action.
   - "Concise answer followed by the key checks" → outputs with a brief answer PLUS an explicit "Key checks:" section.
   - "Compare the main alternatives and state the tradeoff" → outputs with ≥2 named alternatives AND an explicit tradeoff statement.
   - "Explain the main idea, then give one concrete example" → outputs with a clearly delimited fresh example (never copied from any reference).
2. **Fresh-example discipline (~15%):** prompts that tempt parroting (where a reference example exists); outputs must invent a NEW concrete example. Directly targets the 01583 failure mode.
3. **Replay (~15%):** 45–60 of the best format-diverse examples from the v01/v02 corpus, to anchor existing behavior.

**Format:** same JSONL schema as current data (`id, instruction, output, category, skill, difficulty, source="RY3_V03_FORMAT", quality_profile`). Instructions should reuse the eval's exact format-constraint phrasings so the model learns to recognize them.

**Quality rules (extends RY3_ULTRA_QUALITY_RULES.md):**
- R16 (new): Every structural element named in the instruction MUST appear in the output — ordered steps, key checks, tradeoff statement, or concrete example, as applicable. An answer without its required structure is a failure regardless of content quality.
- R17 (new): Examples must be freshly generated for the prompt at hand. Never reproduce a reference answer's example verbatim.
- R18 (new): Format compliance is checked before content scoring during dataset review.

**Size rationale:** the weakness is narrow (19 regressions, one mechanism). A small, surgical dataset is the right tool — not another 2,720-example broad sweep.

## 9. v03 training configurations, ranked by expected value

### Config A — Format-obedience continuation (smallest/cleanest, do this first)
- **Start:** v02 adapter (continue the winning lineage).
- **Data:** ~350 Dataset-3 examples (format-exemplifying + fresh-example + replay mix above).
- **Hyperparameters:** LR **2e-5** (lower than v02's 5e-5 — small targeted fix, minimize disruption), 2 epochs, batch 2×8=16, warmup 100, paged_adamw_8bit, fp32, grad checkpointing on, truncation 2048 (match v02's actual code).
- **Tests:** does targeted format data repair instruction_following on rigid formats without eroding the +8.5% content gains?
- **Expected:** instruction_following on troubleshoot_steps/concise_keychecks rises toward 3.95+; total holds ≥19.5/20.
- **Cost:** 350×2/16 ≈ **44 steps, ~3 minutes** on T4. Essentially free.
- **Go/no-go:** re-run the locked 240 eval; ship only if regressions ≤5 and mean ≥19.4.

### Config B — A + heavier replay (if A shows any forgetting)
- Same as A but dataset = 350 new + 350 replayed v01/v02 examples (700 total), LR 2e-5, 2 epochs.
- **Tests:** whether pure-format data causes content drift; the replay anchors it.
- **Cost:** ~88 steps, ~6 minutes.
- Only run if Config A's eval shows content-score erosion.

### Config C — Broad refresh (only if A/B succeed and you want more)
- 700–800 examples: format-obedience + new coverage of under-trained topic categories (chemistry, biology, astronomy had zero v02-targeted examples; student-audience items gained least at +0.83).
- LR 5e-5, 2 epochs, same stack as v02.
- **Cost:** ~100 steps, ~8 minutes.
- This is the "v02 recipe repeated with better data" — do it only after A proves the mechanism.

**What NOT to do:** do not raise the learning rate above 5e-5 (v01's 1e-4 produced a wash); do not change LoRA rank/alpha (r16/a32 works — don't fix what isn't broken); do not touch the locked 240 eval set.

---

## 10. Honest uncertainties

- The judge is Qwen3-1.7B scoring against reference answers — it rewards reference-alignment. v02's 97.9%-of-max suggests possible **ceiling effects**; future gains may need harder eval items, not just better training.
- Category labels above are derived from instruction phrasing, not the training data's own `category` field — the mapping is approximate.
- Audience-level deltas have small n's; the beginner/student spread (+2.36 vs +0.83) is suggestive, not conclusive.
- The 01583 "parroting" judgment is one data point; whether v02 systematically copies references more than base is unmeasured.
- v01's exact max_seq_length and the v02 base-precision detail (4-bit vs fp16 adapter loading) are unrecoverable from the artifacts — recorded as unknown rather than assumed.
