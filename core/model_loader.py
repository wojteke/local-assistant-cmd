import os
from peft import PeftConfig, PeftModel, get_peft_model, LoraConfig, TaskType
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from typing import Tuple
from core.enums import GPT2Models


# used in different envs when project has different directory
PATH_PREFIX: str = None


def save_model(model: GPT2LMHeadModel | PeftModel, model_name: str, use_lora: bool, epoch: int):
    if PATH_PREFIX is not None:
        path = os.path.join(PATH_PREFIX, "models")
    else:
        path = "models"

    if not os.path.exists(path):
        os.makedirs(path)

    model_save_path = os.path.join("models", "lora", f"{model_name}_lora_epoch_{epoch}") if use_lora else os.path.join(
        "models", "full", f"{model_name}_epoch_{epoch}")

    model.save_pretrained(model_save_path)


def create_gpt2_model(model_name: str, use_lora: bool) -> Tuple[GPT2Tokenizer, GPT2LMHeadModel]:
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    tokenizer.pad_token_id = tokenizer.eos_token_id

    model = GPT2LMHeadModel.from_pretrained(model_name)
    if use_lora:
        peft_config = LoraConfig(task_type=TaskType.CAUSAL_LM,
                                 fan_in_fan_out=True,
                                 inference_mode=False,
                                 r=8,
                                 lora_alpha=32,
                                 lora_dropout=0.1)
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()
    return tokenizer, model


def load_gpt2_model(model_name: str) -> Tuple[GPT2Tokenizer, GPT2LMHeadModel]:
    tokenizer = GPT2Tokenizer.from_pretrained(GPT2Models.gpt2)
    tokenizer.pad_token_id = tokenizer.eos_token_id

    if "lora" in model_name:
        path = os.path.join("models", "lora", model_name)
        return tokenizer, _load_gpt2_lora_model(path)
    else:
        path = os.path.join("models", model_name) + ".pt"
        path = os.path.join("models", "full", model_name)
        return tokenizer, _load_gpt2_model(path)


def _load_gpt2_model(path: str) -> GPT2LMHeadModel:
    model = GPT2LMHeadModel.from_pretrained(path)
    return model


def _load_gpt2_lora_model(path: str) -> GPT2LMHeadModel:
    config = PeftConfig.from_pretrained(path)
    model = GPT2LMHeadModel.from_pretrained(config.base_model_name_or_path)
    model = PeftModel.from_pretrained(model, path)
    return model
