import random
import numpy as np
import torch
import torch.nn as nn 

def count_parameters(model: nn.Module) -> int:
    """
    Counts number of parameters of the model including all nested/hidden modules/layers
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def reset_seeds(seed_val=42):
    """
    Sets seed of all used libs to given value (42 by default)
    """
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)