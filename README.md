# RY3 Fine-Tune

Personal LoRA fine-tuning project on **Qwen3-1.7B** (`saidutta69/Qwen3-1.7B-heretic` base).
Built and trained by Ryan (KING_RY3) using Unsloth on Colab.

## Current status: v02 trained checkpoint

| | |
|---|---|
| Base model | `saidutta69/Qwen3-1.7B-heretic` |
| Method | LoRA (r=16, alpha=32, dropout 0.05) |
| Target modules | q/k/v/o_proj, gate/up/down_proj |
| Training | 2 epochs, lr 5e-5, batch 16 eff., max_len 128, paged_adamw_8bit |
| Result | 340 steps, loss 0.4265, ~22.5 min runtime |
| Train data | 2,720 examples (1,920 v01 + 800 new v02) |
| Locked eval | 240 examples |

## Repo layout

```
notebooks/   Training notebooks (Unsloth/Colab)
data/        Training data, eval sets, judgments, results, manifest
configs/     LoRA adapter config, tokenizer config, chat template, trainer state
docs/        Quality rules and project docs
```

## Notes

- Model weights (`adapter_model.safetensors`, optimizer states, checkpoints) are **not** in this repo — they live on Hugging Face / local storage. See `data/SHA256SUMS.txt` for integrity hashes.
- v02 eval: the automated judge failed to emit parseable scores (`ry3_v02_results.jsonl` holds the raw responses; `ry3_v02_judgments.jsonl` holds the judgment attempts). Eval methodology is a work in progress.
- `docs/RY3_ULTRA_QUALITY_RULES.md` defines the data quality bar for dataset construction.

## Reproducing

1. Open `notebooks/Training.ipynb` in Colab.
2. Point it at `data/RY3_CUMULATIVE_V02_TRAIN.jsonl`.
3. LoRA config matches `configs/adapter_config.json`.
