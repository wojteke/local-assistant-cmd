import json
import os
import random
import torch
import transformers
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import default_data_collator, get_linear_schedule_with_warmup
from peft import get_peft_config, get_peft_model, get_peft_model_state_dict, LoraConfig, TaskType
from tqdm import tqdm
from core.enums import GPT2Models
from datasets import load_dataset
from torch.utils.data import DataLoader
import numpy as np
from core.model_loader import create_gpt2_model, load_gpt2_model, save_model
from training.train_data_loader import get_dataloaders, default_data_path
from training.learning_rate_tools import get_loss_over_lr, find_lr


device = 'cuda' if torch.cuda.is_available() else 'cpu'


class TrainingConfig(object):
    model_name: str
    lr: float
    use_lora: bool
    batch_size: int
    num_epochs: int


def eval_model(tokenizer, model, eval_dataloader):
    model.eval()
    eval_loss = 0
    eval_preds = []
    for step, batch in enumerate(tqdm(eval_dataloader)):
        batch = {k: v.to(device) for k, v in batch.items()}
        with torch.no_grad():
            outputs = model(**batch)
        loss = outputs.loss
        eval_loss += loss.detach().float()
        eval_preds.extend(
            tokenizer.batch_decode(torch.argmax(
                outputs.logits, -1).detach().cpu().numpy()[0], skip_special_tokens=True)
        )

    eval_epoch_loss = eval_loss / len(eval_dataloader)
    eval_ppl = torch.exp(eval_epoch_loss)
    return eval_ppl, eval_epoch_loss


def train_epoch(model, optimizer, lr_scheduler, train_dataloader):
    model.train()
    total_loss = 0
    for batch in tqdm(train_dataloader):
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        total_loss += loss.detach().float()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

    train_epoch_loss = total_loss / len(train_dataloader)
    train_ppl = torch.exp(train_epoch_loss)
    return train_ppl, train_epoch_loss


def train_loop(config: TrainingConfig):
    model_name = config.model_name
    use_lora = config.use_lora
    lr = config.lr
    num_epochs = config.num_epochs
    # batch_size = 4 is ideal for collab - gpt2-small
    batch_size = config.batch_size

    tokenizer, model = create_gpt2_model(model_name, use_lora=use_lora)

    train_dataloader, eval_dataloader = get_dataloaders(
        tokenizer, batch_size=batch_size)

    # optimizer and lr scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    lr_scheduler = get_linear_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=100,
        num_training_steps=(len(train_dataloader) * num_epochs),
    )

    # training and evaluation
    model = model.to(device)
    eval_ppl, eval_epoch_loss = eval_model(tokenizer, model, eval_dataloader)
    print(f"Raw model: {eval_ppl=} {eval_epoch_loss=}")
    for epoch in range(num_epochs):
        train_ppl, train_epoch_loss = train_epoch(
            model, optimizer, lr_scheduler, train_dataloader)
        eval_ppl, eval_epoch_loss = eval_model(
            tokenizer, model, eval_dataloader)
        print(
            f"Epoch: {epoch}: {train_ppl=} {train_epoch_loss=} {eval_ppl=} {eval_epoch_loss=}")
        save_model(model, model_name, use_lora, epoch)


def find_learning_rate(config: TrainingConfig):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    min_lr = 1e-6
    max_lr = 1
    tokenzier, model = create_gpt2_model(config.model_name, config.use_lora)
    model = model.to(device)
    train_dataloader, _ = get_dataloaders(tokenzier, config.batch_size)
    optimizer = torch.optim.AdamW(model.parameters(), lr=min_lr)
    lr_history = get_loss_over_lr(
        model, train_dataloader, optimizer, min_lr, max_lr)

    lora_suffix = '_lora' if config.use_lora else ''
    with open(f'{config.model_name}{lora_suffix}_lr_data.json', 'w') as f:
        json.dump(lr_history, f)

    lower, upper = find_lr(lr_history)
    return (lower + upper)/2


if __name__ == '__main__':
    find_lrs = False
    train_models = True
    models = [GPT2Models.gpt2, GPT2Models.gpt2_medium, GPT2Models.gpt2_large]
    lrs = [5e-4, 5e-4, 5e-4]
    batch_sizes = [8, 4, 2]
    loras = [False, True]
    for model, lr, batch_size in zip(models, lrs, batch_sizes):
        for use_lora in loras:
            seed_val = 42
            random.seed(seed_val)
            np.random.seed(seed_val)
            torch.manual_seed(seed_val)
            torch.cuda.manual_seed_all(seed_val)
            config = TrainingConfig()
            config.model_name = model
            config.use_lora = use_lora
            config.batch_size = batch_size
            config.num_epochs = 3
            if find_lrs:
                config.lr = find_learning_rate(config)
                print(f"model: {config.model_name} optimal lr: {config.lr}")
            else:
                config.lr = lr
            if train_models:
                train_loop(config)
