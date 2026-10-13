# RY3 v03 TRUE Config A training (44-step rerun) — continuation from v02 adapter
# Hyperparameters per Ryan's spec (2026-10-12):
#   LR 2e-5, 2 epochs, per-device batch 2, grad accum 8 (eff batch 16),
#   warmup 100, paged_adamw_8bit, fp32, grad checkpointing ON, max_length 2048
# Dataset: dataset3.jsonl (~349 format-obedience examples)
# Saves to /content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v03_44step (does NOT overwrite the Kaggle 22-step v03)

import json
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
V03_OUTPUT = "/content/drive/MyDrive/RY3/RY3_QWEN3_1.7B_v03_44step"
DATA_PATH = "/content/dataset3.jsonl"

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

print("Loading v02 adapter as trainable (continuation)...", flush=True)
model = PeftModel.from_pretrained(model, V02_ADAPTER, is_trainable=True)
model.print_trainable_parameters()

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Loading and tokenizing Dataset 3...", flush=True)
examples = []
with open(DATA_PATH) as f:
    for line in f:
        line = line.strip()
        if line:
            examples.append(json.loads(line))
print(f"Loaded {len(examples)} examples", flush=True)

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

args = TrainingArguments(
    output_dir=V03_OUTPUT,
    num_train_epochs=2,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    warmup_steps=100,
    learning_rate=2e-5,
    optim="paged_adamw_8bit",
    fp16=False,
    bf16=False,
    gradient_checkpointing=True,
    logging_steps=5,
    save_steps=22,
    save_total_limit=2,
    report_to="none",
    seed=42,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

print("Starting v03 TRUE Config A training (~44 steps, single GPU)...", flush=True)
result = trainer.train()
print(f"Training done. Final loss: {result.training_loss:.5f}", flush=True)

print("Saving v03 adapter...", flush=True)
model.save_pretrained(V03_OUTPUT)
tokenizer.save_pretrained(V03_OUTPUT)

with open(f"{V03_OUTPUT}/V03_TRAINING_REPORT.json", "w") as f:
    json.dump({
        "config": "v03 Config A TRUE (44-step single-GPU rerun)",
        "base_model": BASE_MODEL,
        "starting_adapter": V02_ADAPTER,
        "dataset": DATA_PATH,
        "n_examples": len(examples),
        "learning_rate": 2e-5,
        "epochs": 2,
        "per_device_batch": 2,
        "grad_accum": 8,
        "effective_batch": 16,
        "warmup_steps": 100,
        "optimizer": "paged_adamw_8bit",
        "precision": "fp32",
        "gradient_checkpointing": True,
        "max_length": 2048,
        "final_loss": result.training_loss,
        "global_step": result.global_step,
    }, f, indent=2)

print("V03_TRAINING_SAVED", flush=True)
