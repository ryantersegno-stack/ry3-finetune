# Session notes — 2026-10-11 (RY3 GitHub backup)

## What Ryan asked
Back up his RY3 fine-tuning project from Google Drive to GitHub. Keep notes because he'll forget.

## What was found in Google Drive
- **RY3 project** (folder `RY3/`): v01 and v02 fine-tuning runs on Qwen3-1.7B (base: `saidutta69/Qwen3-1.7B-heretic`)
  - LoRA adapters (`adapter_model.safetensors` 66.5MB), checkpoints (200/340/360), optimizer states
  - `RY3_CUMULATIVE_V02_TRAIN.jsonl` (2.1MB, 2720 examples), `RY3_V02_TARGETED_800`, `RY3_ULTRA_MASTER_DATASET_v01`
  - Eval: `RY3_EVAL_v01/v02`, `ry3_v02_judgments.jsonl`, `ry3_v02_results.jsonl`, `RY3_v02_MANIFEST.json` (240 locked eval examples; note: judge scores marked not valid)
  - `RY3_ULTRA_QUALITY_RULES.md`, `SHA256SUMS.txt`
- **Colab Notebooks**: `Training.ipynb` (Unsloth-based, 267KB), `Untitled2.ipynb` (587KB), `Untitled1.ipynb`
- Also in Drive (not for GitHub): `Clef starter kit.md` (Clef is parked), Prompt pack folder, CoinbaseWalletBackups

## What was downloaded (local: ~/workspace/ry3-github/staging/)
Notebooks, manifest, judgments, results, quality rules, SHA256SUMS, cumulative train jsonl, adapter/tokenizer/trainer configs, chat template, README.

## What was NOT pulled (too large for GitHub — belong on Hugging Face)
- `adapter_model.safetensors` (66.5MB x several copies)
- `optimizer.pt` (34.2MB), `scheduler.pt`, `rng_state.pth`, `training_args.bin`
- `tokenizer.json` (10.9MB — duplicates Qwen3 base tokenizer, loadable from HF)

## Status
- DONE 2026-10-11: repo `ryantersegno-stack/ry3-finetune` (private) created by Ryan. 10 files uploaded: README.md, notebooks/Untitled1.ipynb, data/{RY3_v02_MANIFEST.json, ry3_v02_judgments.jsonl, SHA256SUMS.txt}, configs/{adapter_config.json, tokenizer_config.json, chat_template.jinja, trainer_state.json}, docs/RY3_ULTRA_QUALITY_RULES.md.
- TODO (Ryan, at laptop): 4 large files couldn't go through the CLI (OS arg-size limit) — download from the temp links and drag into the repo via GitHub web "Add file > Upload files". Links expire 2026-10-13:
  - Training.ipynb -> notebooks/Training.ipynb
  - Untitled2.ipynb -> notebooks/Untitled2.ipynb
  - ry3_v02_results.jsonl -> data/ry3_v02_results.jsonl
  - RY3_CUMULATIVE_V02_TRAIN.jsonl -> data/RY3_CUMULATIVE_V02_TRAIN.jsonl
- LATER: model weights (66MB safetensors etc.) belong on Hugging Face, not GitHub.
- DONE 2026-10-11: Gmail cleanup — trashed 1,302 old promos + 4,465 old social notifications (5,767 total), protected banks/Cash App/FL/DCF/personal/attachments per Ryan's rules. Ryan emptied trash himself (CLI blocks permanent deletes). Storage went 15.25 → 15.09 GB.
- DONE 2026-10-11: Google Photos easy cleanup via browser — deleted all blurry photos (~270-300 MB) and all 66 screenshots (~71 MB), move-to-trash only (Photos trash auto-deletes after 30 days). Storage now 13 GB of 15 GB used (2 GB free). Large photos & videos (6.4 GB) untouched — top 10 biggest videos identified, awaiting Ryan's keep/kill decisions.

## Other context from today
- WR3N avatar redesigned via Ryan's "let the AI choose" experiment: fox-hybrid anime baddie, crown, set active 2026-10-11.
- Google storage cleanup: 15GB plan at ~14.2GB used. Drive ~0.9GB, Gmail ~1GB, **Google Photos ~13GB** (videos) is the hog. Awaiting Ryan's choice: WR3N drives Photos in browser, or he DIYs with guidance.
- Suno bulk-download title recovery: parked until Ryan has time.
- Connected today: Gmail, Google Drive, Messenger, Google Calendar, Google Docs, GitHub (ryantersegno-stack, all repos).
