import json
import torch
from torch.optim.lr_scheduler import LRScheduler
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from tqdm import tqdm
from core.enums import GPT2Models
from core.helpers import reset_seeds
from core.model_loader import create_gpt2_model, save_model
from training.train_data_loader import get_dataloaders
from training.learning_rate_tools import get_loss_over_lr, find_lr


DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'


class TrainingConfig(object):
    model_name: str
    lr: float
    use_lora: bool
    batch_size: int
    num_epochs: int


def eval_model(tokenizer: GPT2Tokenizer, model: GPT2LMHeadModel, eval_dataloader: DataLoader):
    model.eval()
    eval_loss = 0
    eval_preds = []
    for step, batch in enumerate(tqdm(eval_dataloader)):
        batch = {k: v.to(DEVICE) for k, v in batch.items()}
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


def train_epoch(model: GPT2LMHeadModel, optimizer: Optimizer, lr_scheduler: LRScheduler, train_dataloader: DataLoader):
    model.train()
    total_loss = 0
    for batch in tqdm(train_dataloader):
        batch = {k: v.to(DEVICE) for k, v in batch.items()}
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
    model = model.to(DEVICE)
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
            reset_seeds()
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
