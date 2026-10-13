# v01-repro anomaly — forensics brief (prepared 2026-10-13 ~15:45 UTC)

**The anomaly:** Reproduced v01 (Branch A Stage 1) scored **19.54/20** on the 48-example
sanity screen vs the expected ~18.00. Per the manifest's stop rule, Stage 2 and Branch B
are stopped pending investigation.

## What was verified (all from local primary records, no Drive needed)

1. **Historical v01's 18.00 is real and on the repaired protocol.**
   `ry3-github/eval_repair/RY3_EVAL_REPAIR_judgments.jsonl` (720 = 3 models × 240):
   - base: 240/240 parsed, mean 18.0333
   - v01: 237/240 parsed, mean **17.9958** — matches the quoted 18.00 exactly
   - v02: 240/240 parsed, mean 19.5708
   - v01's 3 parse failures (RY3-ULTRA-01688, -00506, -00863) can move the mean by
     at most ~0.05 — NOT the explanation.

2. **The 48-example screen is a FIXED subset, fully comparable.**
   `primer_v01repro_screen_eval.py` takes `instructions[::5]` (every 5th of the locked 240)
   — same subset for every screen run, and the judge protocol is verbatim from the
   repaired eval. Cross-checked against the judgment file:
   - base on subset: 17.9583 (screen reported 17.96 ✓)
   - v02 on subset: 19.6250 (screen reported 19.62 ✓)
   So subset and judge are validated — comparability holds.

3. **Historical v01 on that EXACT subset scores 18.125 — the repro's 19.54 is a genuine ~1.4-point outperformance**
   of the same data point the experiment was sanity-checking against. Not a subset artifact,
   not a judge artifact, not a parse-exclusion artifact.

4. **Dataset and adapter already ruled out** by the main agent: v01 repro dataset verified
   clean (1920 RY3-ULTRA, no v02 contamination); eval loaded the reproduced v01 adapter
   (the "v03_512" label was a stale script string).

## What remains different (the actual degrees of freedom)

Historical v01 records only establish: 1920 examples, lr 1e-4, 3 epochs.
NOT recorded for historical v01: max_length, warmup_steps, seed, effective batch size,
optimizer/scheduler details, precision, hardware. The repro used v02's values for all
inferred settings (max_length=128, warmup=100, seed=42, eff batch 16, paged_adamw_8bit,
fp32, grad checkpointing ON) — explicitly flagged in the manifest as inference.

So the entire +1.4 could plausibly live in the settings, not the data — i.e. historical
v01's 18.00 may reflect a weaker config (analogous to how the v03 Run 1's doubled batch
produced 22 steps and loss 8.995), and the "zero standalone gain" premise of the primer
experiment may be an artifact of that config, not a fact about the v01 data.

## Historical v01 per-criterion profile on the 48 subset (for comparison when the repro's arrives)

- correctness 3.729, relevance 3.688, completeness 3.312, instruction_following 3.833,
  reasoning_quality 3.562 (n=48 parsed)
- For reference, v02 on the same subset: 4.000 / 3.958 / 3.917 / 3.938 / 3.812;
  base: 3.646 / 3.667 / 3.396 / 3.812 / 3.438.

## The one check still needed (requires Drive or the next Colab session)

Reproduced v01's per-criterion profile from the screen run —
`/content/drive/MyDrive/RY3/eval_primer_v01repro/v01repro_screen_scoreboard.txt`
(also `v01repro_screen_results.jsonl` / `v01repro_screen_judgments.jsonl`).

**Diagnostic read:** if the repro's gains over historical v01 concentrate in
reasoning_quality/completeness (v02's headroom dimensions), that points at the
SETTINGS doing the work — and kills the primer premise in a different way than the
current hypothesis. If the gains are spread evenly, it looks more like the data was
always good and historical v01 was just misconfigured.

## Suggested next steps (for Ryan's decision)

- Read the repro scoreboard off Drive and compare per-criterion profiles.
- Search Drive/RY3 and any local archives for a v01 training log or notebook that records
  the true max_length/warmup/seed/batch — one such record would settle it directly.
- No further training spend until the anomaly is explained; champion v02 untouched.
