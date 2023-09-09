from math import exp, log
from typing import Tuple
import torch


device = 'cuda' if torch.cuda.is_available() else 'cpu'


def get_loss_over_lr(model, train_dataloader, optimizer, smallest_lr: float, largest_lr: float) -> list[Tuple[float, float]]:
    def update_lr():
        for g in optimizer.param_groups:
            g['lr'] = lr

    def lr_generator(smallest_lr, val):
        return exp(val/10) * smallest_lr
    
    def inv_lr_generator(smallest_lr, val):
        return 10*log(val/smallest_lr)

    number_of_steps = inv_lr_generator(smallest_lr, largest_lr) + 1
    if number_of_steps > len(train_dataloader):
        raise ValueError("Training set too small for this range of lr")
    
    model.train()
    dataloader_iterator = iter(train_dataloader)
    step = 0
    lr = smallest_lr
    history = []

    while (lr < largest_lr):
        lr = lr_generator(smallest_lr, step)
        step += 1
        update_lr()
        batch = next(dataloader_iterator)
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        history.append((lr, loss.item()))
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    return history


def find_lr(history) -> Tuple[float, float]:
    dLr = []
    dLoss = []
    for i in range(len(history)-1):
        lr1, loss1 = history[i]
        lr2, loss2 = history[i+1]
        a = (loss2 - loss1)/(lr2 - lr1)
        dLr.append((lr1, lr2))
        dLoss.append(a)
    min_value = min(dLoss)
    min_index = dLoss.index(min_value)
    return dLr[min_index]
