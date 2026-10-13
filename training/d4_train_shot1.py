# RY3 D4 Shot 1 training — continuation from v02 adapter on validated D4 dataset
# AUTHORIZED config (Rye + Mira, 2026-10-13):
#   start=v02, dataset=RY3_Dataset4_Mira_Curated_FIXED (160), epochs=1, lr=5e-5,
#   eff batch 16, paged_adamw_8bit, fp32, grad checkpointing ON,
#   LoRA r16/alpha32/dropout0.05 on q,k,v,o,gate,up,down_proj
# Mechanical protocol follows the v03 true run (seed 42, max_length 2048,
# per-device batch 2 / grad accum 8, 4-bit NF4 base, chat-template formatting).
# Unspecified mechanical params use TrainingArguments library defaults
# (warmup_steps=0 default lets the specified lr=5e-5 take effect over 10 steps).
# DO NOT retune. One epoch only. No second shot from this script.

import json
import hashlib
import torch
from google.colab import drive

drive.mount('/content/drive')

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
)
from peft import PeftModel, prepare_model_for_kbit_training

BASE_MODEL = "saidutta69/Qwen3-1.7B-heretic"
V02_ADAPTER = "/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v02"
D4_OUTPUT = "/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_D4_shot1"
DATA_PATH = "/content/RY3_Dataset4_Mira_Curated_FIXED_11_b8rc.jsonl"
EXPECTED_SHA256 = "e4d026639da2671f8c71c7abaae38297ca34ce02841a69792e988af3c418b846"

# ---- pre-training verification ----
print("Verifying v02 adapter...", flush=True)
import os
assert os.path.isdir(V02_ADAPTER), f"v02 adapter missing: {V02_ADAPTER}"
assert os.path.exists(os.path.join(V02_ADAPTER, "adapter_model.safetensors")), "v02 safetensors missing"
assert os.path.exists(os.path.join(V02_ADAPTER, "adapter_config.json")), "v02 adapter_config missing"
print("v02 adapter present.", flush=True)

print("Verifying D4 dataset SHA256...", flush=True)
h = hashlib.sha256()
with open(DATA_PATH, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
        h.update(chunk)
actual_sha = h.hexdigest()
print(f"  actual:   {actual_sha}", flush=True)
print(f"  expected: {EXPECTED_SHA256}", flush=True)
assert actual_sha == EXPECTED_SHA256, "DATASET SHA256 MISMATCH — dataset changed, aborting"
print("Dataset SHA256 verified. Dataset unchanged.", flush=True)

print("Loading base model (4-bit NF4)...", flush=True)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16,
)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

print("Loading v02 adapter as trainable (D4 Shot 1 continuation)...", flush=True)
model = PeftModel.from_pretrained(model, V02_ADAPTER, is_trainable=True)
model.print_trainable_parameters()

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Loading and tokenizing D4...", flush=True)
examples = []
with open(DATA_PATH) as f:
    for line in f:
        line = line.strip()
        if line:
            examples.append(json.loads(line))
print(f"Loaded {len(examples)} examples", flush=True)
assert len(examples) == 160, f"expected 160 examples, got {len(examples)}"

def format_and_tokenize(ex):
    messages = [
        {"role": "user", "content": ex["instruction"]},
        {"role": "assistant", "content": ex["output"]},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return tokenizer(text, truncation=True, max_length=2048)

tokenized = [format_and_tokenize(ex) for ex in examples]
lengths = [len(t["input_ids"]) for t in tokenized]
print(f"Token lengths: min={min(lengths)} max={max(lengths)} mean={sum(lengths)/len(lengths):.1f}", flush=True)

class DictDataset(torch.utils.data.Dataset):
    def __init__(self, items):
        self.items = items
    def __len__(self):
        return len(self.items)
    def __getitem__(self, i):
        return {k: torch.tensor(v) for k, v in self.items[i].items()}

train_dataset = DictDataset(tokenized)

# 160 examples / eff batch 16 = 10 optimizer steps, 1 epoch
args = TrainingArguments(
    output_dir=D4_OUTPUT,
    num_train_epochs=1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=5e-5,
    optim="paged_adamw_8bit",
    fp16=False,
    bf16=False,
    gradient_checkpointing=True,
    logging_steps=2,
    save_steps=10,
    save_total_limit=1,
    report_to="none",
    seed=42,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

print("Starting D4 Shot 1 training (10 steps, 1 epoch)...", flush=True)
result = trainer.train()
print(f"Training done. Final loss: {result.training_loss:.5f}", flush=True)
print(f"Global steps: {result.global_step}", flush=True)

print("Saving D4 Shot 1 adapter...", flush=True)
model.save_pretrained(D4_OUTPUT)
tokenizer.save_pretrained(D4_OUTPUT)

with open(f"{D4_OUTPUT}/D4_SHOT1_TRAINING_REPORT.json", "w") as f:
    json.dump({
        "shot": "RY3 QWEN3-1.7B D4 SHOT 1",
        "base_model": BASE_MODEL,
        "starting_checkpoint": V02_ADAPTER,
        "starting_model": "v02",
        "dataset_filename": "RY3_Dataset4_Mira_Curated_FIXED_11_b8rc.jsonl",
        "dataset_sha256": actual_sha,
        "dataset_sha256_verified": True,
        "n_examples": len(examples),
        "learning_rate": 5e-5,
        "epochs": 1,
        "per_device_batch_size": 2,
        "gradient_accumulation_steps": 8,
        "effective_batch_size": 16,
        "warmup_steps": 0,
        "warmup_note": "TrainingArguments default; specified config had no warmup; default lets lr=5e-5 take effect over 10 steps",
        "optimizer": "paged_adamw_8bit",
        "precision": "fp32",
        "gradient_checkpointing": True,
        "max_length": 2048,
        "seed": 42,
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05,
                 "targets": ["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
                 "note": "continued v02 adapter weights directly (v02 adapter_config verified r=16/alpha=32/dropout=0.05, same 7 targets)"},
        "global_steps": result.global_step,
        "final_loss": result.training_loss,
        "output_adapter_path": D4_OUTPUT,
    }, f, indent=2)

print("D4_TRAINING_SAVED", flush=True)
