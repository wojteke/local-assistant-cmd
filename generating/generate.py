import asyncio
from collections import deque
from queue import Queue
import threading
from typing import Callable
import torch
from core.enums import Headers
from core.prompter import generate_prompt, get_last_response
from transformers import StoppingCriteria, StoppingCriteriaList
from transformers import GPT2LMHeadModel, GPT2Tokenizer

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
QUEUE_BUFFOR_LENGTH = 3

class KeywordsStoppingCriteria(StoppingCriteria):
    def __init__(self, stops: list[torch.Tensor] = [], device: str = None):
        super().__init__()
        self.stops = [stop.to(DEVICE if device == None else device)
                      for stop in stops]

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        for stop in self.stops:
            if torch.all((stop == input_ids[0][-len(stop):])).item():
                return True
        return False


class ExternalStoppingCriteria(StoppingCriteria):
    def __init__(self, on_token: Callable[[torch.LongTensor], None]):
        self.on_token = on_token

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        self.on_token(input_ids[0])
        return False


def get_response(
        model: GPT2LMHeadModel,
        tokenizer: GPT2Tokenizer,
        stopping_criteria: StoppingCriteria,
        conversation: list[str],
        temperature: float = 1,
        top_p=0.5,
        top_k=50,
        num_return_sequences=1,
        max_new_tokens=150):

    prompt = generate_prompt(conversation, add_ai_token=True)
    encoded = tokenizer(prompt, return_tensors='pt')
    encoded = encoded.to(DEVICE)

    generation_params = {
        "input_ids": encoded['input_ids'],
        "attention_mask": encoded['attention_mask'],
        "pad_token_id": tokenizer.pad_token_id,
        "do_sample": True,
        "temperature": temperature,
        "top_k": top_k,
        "max_new_tokens": min(max_new_tokens, 1024-len(encoded['input_ids'][0])),
        "top_p": top_p,
        "num_return_sequences": num_return_sequences,
    }
    if stopping_criteria is not None:
        generation_params.update({
            "stopping_criteria": StoppingCriteriaList([stopping_criteria])
        })

    generation_output = model.generate(**generation_params)

    s = generation_output[0]
    output = tokenizer.decode(s, skip_special_tokens=True)
    output = output.removesuffix(Headers.user)
    return get_last_response(output)


async def get_response_stream(
        model: GPT2LMHeadModel,
        tokenizer: GPT2Tokenizer,
        stopping_criteria: StoppingCriteria,
        conversation: list[str],
        temperature: float = 1,
        top_p=0.5,
        top_k=50,
        num_return_sequences=1,
        max_new_tokens=150):

    prompt = generate_prompt(conversation, add_ai_token=True)
    encoded = tokenizer(prompt, return_tensors='pt')
    encoded = encoded.to(DEVICE)

    q = Queue()

    def queue_appender(input_ids: torch.LongTensor):
        q.put(input_ids)

    yielding_criteria = ExternalStoppingCriteria(queue_appender)
    stopping_criterias = [yielding_criteria]
    if stopping_criteria is not None:
        stopping_criterias.append(stopping_criteria)

    generation_params = {
        "input_ids": encoded['input_ids'],
        "attention_mask": encoded['attention_mask'],
        "pad_token_id": tokenizer.pad_token_id,
        "do_sample": True,
        "temperature": temperature,
        "top_k": top_k,
        "max_new_tokens": min(max_new_tokens, 1024-len(encoded['input_ids'][0])),
        "top_p": top_p,
        "num_return_sequences": num_return_sequences,
        "stopping_criteria": StoppingCriteriaList(stopping_criterias)
    }

    def worker():
        model.generate(**generation_params)
        q.put(None)

    worker_thread = threading.Thread(target=worker)
    worker_thread.start()
    buffer = deque(maxlen=QUEUE_BUFFOR_LENGTH)
    message = prompt
    while True:
        item = q.get()
        await asyncio.sleep(0.2)
        if item is None:
            break
        new_tokens = tokenizer.decode(item, skip_special_tokens=True)
        diff = new_tokens.removeprefix(message)
        buffer.append(diff)
        if len(buffer) == QUEUE_BUFFOR_LENGTH:
            buffered = "".join(buffer)
            if Headers.user in buffered:
                last_tokens = buffered[:buffered.index(Headers.user)].rstrip()
                if last_tokens != "":
                    yield last_tokens
                break
            yield buffer[0]
        message += diff

    worker_thread.join()
