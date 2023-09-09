import os
from typing import Tuple
from datasets import load_dataset, DatasetDict
from torch.utils.data import DataLoader
from transformers import default_data_collator
from core.prompter import generate_prompt

def default_data_path():
    return os.path.join("data", "cmd_assistant_data_large.json")

def get_eval_dataset(data_path=None) -> DatasetDict:
    if data_path is None:
        data_path = default_data_path()
    # loading dataset
    dataset = load_dataset("json", data_files=data_path)
    dataset = dataset["train"].train_test_split(test_size=0.1)
    dataset["validation"] = dataset["test"]
    del dataset["test"]
    del dataset["train"]
    return dataset

def get_dataloaders(tokenizer, batch_size, data_path=None) -> Tuple[DataLoader, DataLoader]:
    if data_path is None:
        data_path = default_data_path()
    # loading dataset
    dataset = load_dataset("json", data_files=data_path)

    dataset = dataset["train"].train_test_split(test_size=0.1)
    dataset["validation"] = dataset["test"]
    del dataset["test"]

    def preprocess_function(examples):
        conversation = examples['conversation']
        prompt = generate_prompt(conversation)
        model_inputs = tokenizer(
            prompt, padding="max_length", truncation=True, return_tensors="pt")
        model_inputs["labels"] = model_inputs["input_ids"].clone()
        return model_inputs

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
        train_dataset, shuffle=True, collate_fn=default_data_collator, batch_size=batch_size, pin_memory=True)
    
    eval_dataloader = DataLoader(
        eval_dataset, collate_fn=default_data_collator, batch_size=batch_size, pin_memory=True)
    
    return train_dataloader, eval_dataloader
