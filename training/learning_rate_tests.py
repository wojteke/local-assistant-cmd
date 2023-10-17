from learning_rate_tools import find_lr, get_loss_over_lr
from core.model_loader import create_gpt2_model
from core.enums import GPT2Models
import torch
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import default_data_collator
from core.prompter import generate_prompt
import json


device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_name = GPT2Models.gpt2
batch_size = 1
smallest_lr = 1e-5
largest_lr = 1
tokenizer, model = create_gpt2_model(model_name, use_lora=False)
model = model.to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=smallest_lr)

dataset = load_dataset("json", data_files="cmd_assistant_data.json")

dataset = dataset["train"].train_test_split(test_size=0.1)
dataset["validation"] = dataset["test"]
del dataset["test"]
dataset["train"][0]
# causing issues for some reasons
# tokenizer.padding_side = 'left'


def preprocess_function(examples):
    conversation = examples['conversation']
    prompt = generate_prompt(conversation)
    model_inputs = tokenizer(prompt, padding="max_length",
                             truncation=True, return_tensors="pt")
    model_inputs["labels"] = model_inputs["input_ids"].clone()
    return model_inputs


encoded = preprocess_function(dataset['train'][0])
processed_datasets = dataset.map(
    preprocess_function,
    batched=False,
    num_proc=1,
    remove_columns=dataset["train"].column_names,
    load_from_cache_file=False,
    desc="Running tokenizer on dataset",
)

train_dataset = processed_datasets["train"]
eval_dataset = processed_datasets["validation"]
train_dataloader = DataLoader(
    train_dataset, shuffle=True, collate_fn=default_data_collator, batch_size=batch_size, pin_memory=True
)


history = get_loss_over_lr(model, train_dataloader,
                           optimizer, smallest_lr, largest_lr)
lower_lr, higher_lr = find_lr(history)
average_lr = (lower_lr + higher_lr) / 2

with open(f'{model_name}_lr_data.json', 'w') as f:
    json.dump(history, f)
