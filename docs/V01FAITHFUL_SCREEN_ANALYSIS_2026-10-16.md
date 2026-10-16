# Faithful-v01 48-Example Screen: Detailed Analysis
**Date:** 2026-10-16
**Analyst:** WR3N
**Directive:** V01FAITHFUL_FREEZE_DIRECTIVE_2026-10-16.md

---

## Summary

Faithful-v01 (19.71/20) and v02 (19.62/20 on same 48) are **essentially tied**. The 0.09 gap is noise. But the *pattern* of where each wins and loses reveals exactly where the headroom is.

---

## 1. Examples Where Faithful-v01 Beats v02 (6)

| Example | v01 | v02 | Diff | Topic |
|---|---|---|---|---|
| RY3-ULTRA-01514 | 19 | 16 | +3 | Spectrum / astronomers (practitioner) |
| RY3-ULTRA-01822 | 20 | 17 | +3 | Linked list vs array iteration |
| RY3-ULTRA-00388 | 19 | 17 | +2 | Selection bias (analyst, compare alternatives) |
| RY3-ULTRA-02116 | 20 | 18 | +2 | Observation vs inference in images |
| RY3-ULTRA-00928 | 17 | 16 | +1 | Feedback loops / unexpected behavior |
| RY3-ULTRA-01404 | 20 | 19 | +1 | Measurements with timestamps |

**Pattern:** v01 wins on technical explanation questions where a direct, correct answer suffices. It doesn't overcomplicate.

## 2. Examples Where v02 Beats Faithful-v01 (5)

| Example | v01 | v02 | Diff | Topic |
|---|---|---|---|---|
| RY3-ULTRA-01725 | 17 | 20 | -3 | Network failure troubleshooting (structured guide) |
| RY3-ULTRA-01526 | 18 | 20 | -2 | Astronomers studying the past via light (tradeoff analysis) |
| RY3-ULTRA-01399 | 18 | 19 | -1 | Measurements with timestamps (concrete example required) |
| RY3-ULTRA-01469 | 19 | 20 | -1 | Nominal vs real values (compare alternatives) |
| RY3-ULTRA-01885 | 19 | 20 | -1 | Algorithm validation (compare alternatives + tradeoffs) |

**Pattern:** v02 wins wherever the instruction demands *going beyond the correct answer* — structured guides, tradeoff comparisons, concrete examples.

## 3. The 5 v01-vs-v02 Regressions (Individual)

### RY3-ULTRA-01725 (gap: 3 — largest)
- **Instruction:** Why should clients avoid assuming every network failure means server rejection? (Provide structured troubleshooting guide)
- **v01:** 17/20 — correctness 4, relevance 4, completeness 3, instruction_following 3, reasoning 3
- **v02:** 20/20
- **Failure:** "Correctly identifies the timeout scenario and main uncertainty but lacks troubleshooting steps, failing to meet the instruction's requirement for a structured guide."
- **Category:** Instruction-following failure + completeness failure. The model knew the answer but didn't produce the requested *format*.

### RY3-ULTRA-01526 (gap: 2)
- **Instruction:** Why do astronomers use light from distant objects to study the past? (Practitioner, tradeoff analysis expected)
- **v01:** 18/20 — completeness 3, reasoning 3 (vs v02's 4/4)
- **Failure:** "Correctly explains the principle but lacks the tradeoff analysis required by the question."
- **Category:** Reasoning failure. Correct principle, missing analytical depth.

### RY3-ULTRA-01399 (gap: 1)
- **Instruction:** Why record measurements with timestamps? (Beginner, give one concrete example)
- **v01:** 18/20 — completeness 3 (vs v02's 4)
- **Failure:** "Provided the correct answer but did not include a concrete example as required."
- **Category:** Completeness failure. The instruction explicitly asked for an example; the model skipped it.

### RY3-ULTRA-01469 (gap: 1)
- **Instruction:** Distinguish nominal vs real values. (Student, compare alternatives)
- **v01:** 19/20 — reasoning 3 (vs v02's 4)
- **Failure:** "Correctly identifies the distinction but lacks comparison of alternatives."
- **Category:** Reasoning failure. The "compare" in the instruction was not honored.

### RY3-ULTRA-01885 (gap: 1)
- **Instruction:** How to validate an algorithm? (Beginner, compare main alternatives, state tradeoffs)
- **v01:** 19/20 — correctness 3 (vs v02's 4)
- **Failure:** "Provided the correct validation method but omitted the tradeoff comparison required by the instruction."
- **Category:** Correctness failure (per judge) + reasoning failure. The instruction said "compare" and "tradeoffs" — the model gave one method.

## 4. The 2 v01-vs-Base Regressions (Individual)

### RY3-ULTRA-01399 (gap: 1)
- Same as above. Even the base model included the concrete example; v01 did not.
- **This is the most concerning regression** — losing to base on any example warrants attention.

### RY3-ULTRA-01469 (gap: 1)
- Same as above. Base included the alternative comparison; v01 did not.

## 5. Per-Criterion Comparison

| Criterion | v01 | v02 | Base | v01 − v02 |
|---|---|---|---|---|
| Correctness | 3.979 | 4.000 | 3.646 | −0.021 |
| Relevance | 4.000 | 3.958 | 3.667 | +0.042 |
| Completeness | 3.917 | 3.917 | 3.396 | +0.000 |
| Instruction following | 3.979 | 3.938 | 3.812 | +0.042 |
| Reasoning quality | 3.833 | 3.812 | 3.438 | +0.021 |

**v01 is at or above v02 on 4 of 5 criteria.** The models are functionally equivalent at the criterion level.

## 6. Recurring Strengths and Weaknesses

### Strengths (where v01 excels)
- **Direct technical explanations:** When the question wants a correct, clear answer, v01 delivers.
- **Relevance (4.000/4, zero sub-4s):** v01 never goes off-topic. Every response is on-point.
- **Instruction following (3.979/4):** Slightly *above* v02. v01 generally does what's asked.

### Weaknesses (where v01 drops points)
The error pattern is remarkably consistent across all 7 reasoning_quality sub-4s and 4 completeness sub-4s:

1. **Missing tradeoff/alternative comparisons** (dominant — 4x in reasoning, 2x in completeness)
   - When instructions say "compare," "tradeoffs," or "alternatives," v01 gives the correct answer but doesn't compare.
2. **Missing concrete examples** (1x completeness, 1x reasoning)
   - When instructions say "give an example," v01 sometimes skips it.
3. **Missing structured steps/guides** (1x completeness, 1x instruction_following, 2x reasoning)
   - When instructions want a guide or steps, v01 gives prose instead.

## 7. Error Categorization

| Category | Count | Examples |
|---|---|---|
| Reasoning failures (missing tradeoffs/comparisons) | 5 | 01526, 01469, 01885, +2 more |
| Completeness failures (missing examples) | 2 | 01399 (+1 more) |
| Instruction-following failures (wrong format) | 1 | 01725 |
| Knowledge/correctness failures | 0 | — (v01 was never factually wrong) |
| Formatting failures | 0 | — |

**Critical observation:** v01 was **never factually wrong** on any of the 48 examples. Every point dropped was about *going further* — adding comparisons, examples, structure — not about getting the answer right. The model knows the material; it doesn't always deliver the full package the instruction requests.

---

## Headroom Assessment

This is the **same weakness pattern** as v02's weakness map (reasoning_quality 3.80, completeness 3.88 — "shallow reasoning, missing tradeoffs/alternatives"). Both models share it because both were trained on data with the same gap.

**The remaining headroom is clear and specific:**
- Teach the model to include tradeoff/alternative comparisons when instructions say "compare"
- Teach it to include concrete examples when instructions say "give an example"
- Teach it to produce structured steps/guides when instructions request that format

This is **not** a knowledge problem. It's a **response-completeness** problem. The model knows the answers; it needs to learn to deliver the full requested package.

**This is exactly what D4 Shot 1 was designed to target** — and D4 failed (16.4/20, template collapse). The D4 approach (demonstrating troubleshooting steps, tradeoff analysis, concrete examples inside high-quality answers) was the right *idea* but the wrong *execution* (format drilling caused the collapse).

Any future dataset intervention should target these specific gaps **without** falling into template drilling. The v01 data got the model to 19.71 by being natural and high-quality; the next dataset must preserve that naturalness while adding the missing behaviors.

---

## Freeze Status

Per V01FAITHFUL_FREEZE_DIRECTIVE_2026-10-16.md:
- ✅ Adapter preserved in Drive (RY3/RY3_PRIMER_V01FAITHFUL/)
- ✅ Checkpoints preserved (checkpoint-200, checkpoint-360)
- ✅ Training report preserved (V01FAITHFUL_TRAINING_REPORT.json)
- ✅ 48-example judgments preserved (downloaded to workspace)
- ✅ 48-example results preserved (downloaded to workspace)
- ✅ Scoreboard preserved (in Drive)
- ✅ Dataset SHA256: 324610f73fe1afb7a2eff72811da23b8af587d13c48dfbf964db62f64393198b
- ✅ Training config documented (see diagnostic report)

**No training, merging, or modification authorized until next hypothesis is defined.**
