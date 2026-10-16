# RY3 NEXT STEP: FREEZE THE FAITHFUL V01
**Date:** 2026-10-16
**Source:** Ryan (with Mira)
**Status:** ACTIVE DIRECTIVE

The faithful v01 diagnostic is complete.

Result: 19.71/20 on the 48-example locked screen.

Do NOT continue training the faithful-v01 adapter yet. Do NOT merge additional datasets into it. Do NOT overwrite or modify the existing adapter/checkpoints.

## Current status

- Faithful v01: 19.71/20 screen
- v02: 19.57/20 full locked eval
- Base: 17.96/20 screen
- Faithful v01 regressions vs base: 2/48
- Faithful v01 regressions vs v02: 5/48
- Faithful v01 training: 360/360 steps
- Final loss: 0.9819
- Training configuration was faithful to the historical v01 configuration.
- The Primer Theory premise is now dissolved because v01 independently produces a ~19.5–19.7 result.

## Immediate objective

Before doing any additional training, establish exactly what this model has achieved and whether it can be improved without destroying its current behavior.

Run an analysis of the completed 48-example screen:

1. Identify every example where faithful-v01 beats v02.
2. Identify every example where v02 beats faithful-v01.
3. Identify the 5 v01-vs-v02 regressions individually.
4. Identify the 2 v01-vs-base regressions individually.
5. Compare per-criterion behavior.
6. Look for recurring strengths or weaknesses in the v01 outputs.
7. Determine whether the remaining errors appear to be:
   - knowledge/correctness failures
   - completeness failures
   - instruction-following failures
   - reasoning failures
   - formatting failures
   - or something else.

## Critical rule

Do not train based on speculation.

The 19.71 result is now the baseline we must protect.

The next experiment should have a clear hypothesis, a defined dataset intervention, a defined success criterion, and a regression gate before compute is spent.

## Recommended experimental sequence

### Experiment 1: Full locked evaluation

If the existing faithful-v01 adapter can be evaluated against the complete locked 240-example evaluation without altering it, do that first.

The 48-example screen is evidence, but it is not directly comparable to v02's validated 19.57 full-evaluation score.

The goal is to establish the faithful-v01 full-eval score.

### Experiment 2: Error-directed improvement

Only after the full score is established should we consider another training stage.

Use the actual v01 failure cases to design the next dataset rather than blindly continuing with more v01 data.

The objective should be: "improve the weakest dimensions while preserving v01's existing strengths."

Do not assume more training is automatically better.

## Hard regression gate

Any continuation must be rejected if it causes substantial regression.

Use the locked evaluation and require:

- meaningful score improvement
- no broad degradation of existing criteria
- regression count within the established gate
- preservation of v01's strong behavior

If a continuation scores lower or produces widespread regressions, discard it and return to the frozen faithful-v01 adapter.

## Important

Preserve the following permanently:

- faithful-v01 final adapter
- checkpoint-200
- checkpoint-360
- training report
- 48-example judgments
- 48-example results
- scoreboard
- exact dataset SHA256
- exact training configuration

This model is now an experimental control.

Do not touch the control until the next hypothesis is defined.

The next question is not: "What can we train into it?"

The next question is: "What exactly makes this 1.7B model score ~19.7, and where is its remaining headroom?"
