# v03 44-step re-eval — verdict follow-through brief
Prepared by WR3N (research stage), 2026-10-13 ~00:50 UTC.
Veredic verdict expected ~01:52 UTC (19:52 Ryan's time) from the paid-Colab-T4 run launched ~23:52 UTC.

## What this run was testing
- The first v03 attempt (Kaggle, 22 optimizer steps, double effective batch of 32) NO-GO'd at **18.29/20** with **75 regressions** (gates: ≥19.4 mean, ≤5 regressions). Final loss **8.995** vs v02's 0.426.
- Prime suspect: the 22-step double-batch schedule, not the data. The rerun restores true Config A.
- The 44-step rerun (verified in notebook, Drive: `RY3/RY3_QWEN3_1.7B_v03_44step`): **44/44 steps, 2 epochs, final loss 3.789**, healthy descending curve (4.84 → 2.76). Adapter saved to Drive.
- 44-step config (from `v03_train_configA_44step.py`, lines 3–4, 85–89): LR 2e-5, 2 epochs, per-device batch 2, grad accum 8 (eff 16), warmup 100, paged_adamw_8bit, fp32, grad checkpointing ON, truncation max_length 2048. Continued from the v02 adapter.

## If GO (mean ≥19.4/20 AND ≤5 regressions)
v03-44step becomes champion, dethroning v02 (19.57/20, 720-judgment repaired eval).
1. **Scoreboard:** record the 44-step config above into the hyperparameter record (§7 of `V03_ANALYSIS_AND_DATASET3_SPEC.md`); file the judgments file alongside `v02_results.jsonl` / `v03` artifacts in `eval_repair/`.
2. **Retire the failed artifact:** the 22-step Kaggle adapter (`RY3_QWEN3_1.7B_v03.zip` in `~/workspace/browser_downloads/sess-411856308/`, 158MB, loss 8.995) is superseded — mark/rename so it's never mistaken for the champion. The champion lives at Drive `RY3/RY3_QWEN3_1.7B_v03_44step`.
3. **Privacy:** ask Ryan about re-locking the link-shared `RY3/v03_inputs` Drive folder (already queued as a post-verdict item — fold it in here).
4. **Next experiment (his call):** per the spec's ranked configs, Config C (broad refresh, ~700–800 examples incl. chemistry/biology/astronomy, LR 5e-5) only makes sense after A proves the mechanism; OR pivot to the planned "big brain, small body" distillation experiment (memory: distill a larger model into a small one + quantize, benchmark CPU-only). Also note honest ceiling risk: v02 at 19.57 is 97.9% of max on this judge — future gains may need harder eval items, not more training (spec §10).
5. **GPU accounting (delivery-time check):** $9.99 = 100 compute units, 90-day expiry. The 44-step train (~minutes) + ~2h T4 eval consumed some; verify remaining balance with Ryan in the Colab notebook when convenient. Nothing urgent.

## If NO-GO
The schedule hypothesis is dead — the data is now the suspect. Diagnostic ladder:
1. **Compare per-criterion vs the failed 22-step run** (22-step numbers: correctness 3.758, relevance 3.725, completeness 3.458, instruction_following 3.800, reasoning 3.550).
   - If completeness/reasoning **recovered** toward v02 (3.879/3.804) but gates still miss → the schedule was the whole problem and Dataset 3 is directionally right; consider a cleaner rerun or slightly longer Config A.
   - If completeness/reasoning **still depressed** → Dataset 3's outputs themselves are thin. Audit `eval_repair/dataset3.jsonl` (349 examples) for content quality vs the v02 corpus; the format drilling may have come at the cost of substance (the 22-step instruction_following held at 3.800 while content dropped — the format fix worked, the content got diluted).
2. **v04 options:** Config B (same as A + 350 replayed v01/v02 examples, LR 2e-5) to anchor content; or a rebalanced Dataset 3 with richer outputs; do NOT raise LR above 5e-5 (v01's 1e-4 was a wash), do NOT change LoRA r16/a32.
3. **Regression detail:** if regressions cluster on format-rigid categories (troubleshoot_steps, concise_keychecks) per the v02 analysis §5, Dataset 3's format exemplars need tightening, not more of them.

## Open / to check at delivery
- Verdict numbers themselves (main agent owns the Colab browser task; do NOT duplicate-check it here).
- Colab compute-unit balance (needs Ryan's logged-in notebook — ask, don't guess).
- Whether the ~2h eval estimate holds (launched 23:52 UTC; verdict ~01:52 UTC).
