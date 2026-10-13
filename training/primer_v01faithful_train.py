# Historical-faithful v01 reproduction — diagnostic run
# Purpose: determine whether historical v01's 18.00 was caused by its training
# config (fp16 + SFTTrainer default max_seq_length) rather than the data.
# Matches the recovered historical config from staging/Untitled2.ipynb:
#   fp16=True, SFTTrainer, max_seq_length NOT SET (TRL default), lr 1e-4,
#   3 epochs, eff batch 16, warmup 100, paged_adamw_8bit, seed 42,
#   LoRA r16/a32/d0.05, 7 targets, chat-template formatting.
# Differs from primer_branchA_v01repro_train.py ONLY in:
#   fp16=True (was fp32), SFTTrainer (was manual Trainer), no max_length cap.
# Output: /content/drive/MyDrive/RY3/RY3_PRIMER_V01FAITHFUL (isolated; v02 champion untouched)
# NOTE: Drive is mounted separately in the notebook. Do NOT call drive.mount() here.

import json, os, hashlib, torch, transformers, peft, trl
from datasets import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
                          TrainingArguments)
from peft import LoraConfig
from trl import SFTTrainer

BASE_MODEL = "saidutta69/Qwen3-1.7B-heretic"
DATA_PATH = "/content/dataset_v01_1920.jsonl"
EXPECTED_SHA256 = "324610f73fe1afb7a2eff72811da23b8af587d13c48dfbf964db62f64393198b"
OUT_DIR = "/content/drive/MyDrive/RY3/RY3_PRIMER_V01FAITHFUL"
SEED = 42

os.makedirs(OUT_DIR, exist_ok=True)

print("=== environment ===", flush=True)
print(f"torch {torch.__version__}, cuda {torch.version.cuda}", flush=True)
print(f"transformers {transformers.__version__}", flush=True)
print(f"peft {peft.__version__}", flush=True)
print(f"trl {trl.__version__}", flush=True)

# --- dataset hash verification ---
h = hashlib.sha256()
with open(DATA_PATH, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        h.update(chunk)
actual = h.hexdigest()
print(f"dataset sha256: {actual}", flush=True)
assert actual == EXPECTED_SHA256, f"DATASET HASH MISMATCH: {actual}"

# --- model ---
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                         bnb_4bit_compute_dtype=torch.float16,
                         bnb_4bit_use_double_quant=True)
tok = AutoTokenizer.from_pretrained(BASE_MODEL)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL, quantization_config=bnb, device_map="auto")
# NOTE: no explicit torch_dtype — let the 4-bit quant config + fp16=True AMP
# handle dtypes via the framework's standard workflow. Manual dtype forcing
# was fighting torch 2.11's GradScaler expectations.
print(f"model dtype check: {next(model.parameters()).dtype}", flush=True)
# NOTE: historical notebook did NOT call prepare_model_for_kbit_training.
# SFTTrainer + peft_config handles the wrapping, exactly as historical.

lora_cfg = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"])
# NOTE: do NOT pre-wrap with get_peft_model — pass the base model + peft_config
# to SFTTrainer and let it wrap, exactly as the historical notebook did.
# (TRL >= 1.x rejects PeftModel + peft_config together.)
model.print_trainable_parameters() if hasattr(model, "print_trainable_parameters") else None
print(f"base model params: {sum(p.numel() for p in model.parameters())/1e9:.3f}B", flush=True)

# --- data: chat-template formatting (same as historical) ---
rows = []
with open(DATA_PATH) as f:
    for line in f:
        d = json.loads(line)
        rows.append({"instruction": d["instruction"], "output": d["output"]})
print(f"examples: {len(rows)}", flush=True)
assert len(rows) == 1920

def format_example(ex):
    return {"text": tok.apply_chat_template(
        [{"role": "user", "content": ex["instruction"]},
         {"role": "assistant", "content": ex["output"]}],
        tokenize=False, add_generation_prompt=False)}

ds = Dataset.from_list(rows).map(format_example,
                                 remove_columns=["instruction", "output"])

# --- training args: faithful to historical (fp16=True, warmup 100) ---
args = TrainingArguments(
    output_dir=OUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=1e-4,
    warmup_steps=100,
    logging_steps=10,
    save_strategy="steps",
    save_steps=200,
    save_total_limit=2,
    fp16=True,
    bf16=False,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    seed=SEED,
    report_to="none",
    remove_unused_columns=False,
)

# --- SFTTrainer WITHOUT max_seq_length (historical behavior) ---
trainer = SFTTrainer(
    model=model,
    args=args,
    train_dataset=ds,
    peft_config=lora_cfg,
    processing_class=tok,
    # NOTE: max_seq_length intentionally NOT set — reproduces historical default
)
# Resolve max_seq_length the way TRL does (compatible across versions).
# Historical runs did not set it, so TRL falls back to its default.
_resolved_msl = getattr(trainer, "max_seq_length", None)
if _resolved_msl is None:
    _resolved_msl = getattr(getattr(trainer, "args", None), "max_seq_length", None)
if _resolved_msl is None:
    _resolved_msl = getattr(tok, "model_max_length", "unknown")
print(f"SFTTrainer max_seq_length (resolved): {_resolved_msl}", flush=True)
trainer.model.print_trainable_parameters()

print("=== training start ===", flush=True)
result = trainer.train()
print(f"Training done. {result}", flush=True)

print("Saving faithful v01 adapter...", flush=True)
trainer.save_model(OUT_DIR)
tok.save_pretrained(OUT_DIR)

report = {
    "objective": "historical-faithful v01 reproduction (diagnostic)",
    "base_model": BASE_MODEL,
    "dataset_sha256": actual,
    "n_examples": 1920,
    "config": {
        "trainer": "trl.SFTTrainer",
        "max_seq_length_set": False,
        "max_seq_length_resolved": _resolved_msl,
        "fp16": True, "bf16": False,
        "lr": 1e-4, "epochs": 3, "warmup_steps": 100, "seed": 42,
        "per_device_batch": 2, "grad_accum": 8, "eff_batch": 16,
        "optim": "paged_adamw_8bit", "grad_checkpointing": True,
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05,
                 "targets": ["q_proj","k_proj","v_proj","o_proj",
                             "gate_proj","up_proj","down_proj"]},
    },
    "versions": {
        "torch": torch.__version__, "cuda": torch.version.cuda,
        "transformers": transformers.__version__,
        "peft": peft.__version__, "trl": trl.__version__,
    },
    "train_result": str(result),
}
json.dump(report, open(os.path.join(OUT_DIR, "V01FAITHFUL_TRAINING_REPORT.json"), "w"), indent=1)
print("V01FAITHFUL_TRAINING_SAVED", flush=True)
