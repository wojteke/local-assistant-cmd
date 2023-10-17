import json
import os
import torch
from analysis.helpers import make_predictions
from core.enums import Headers
from transformers import StoppingCriteriaList, GPT2Tokenizer
from generating.generate import KeywordsStoppingCriteria


DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
limit = 1


def evaluate(model_name: str, stopping_criteria: StoppingCriteriaList, data: list):
    predictions = make_predictions(model_name=model_name, stopping_criteria=stopping_criteria, data=data, limit=limit, device=DEVICE)

    path = os.path.join('human_tests', f'{model_name}_answers_data.json')
    with open(path, 'w') as f:
        json.dump(predictions, f)

    predicted = []
    references = []
    for conversation in predictions[:limit]:
        for question, pa in conversation:
            prediction, answer = pa
            predicted.append(prediction)
            references.append(answer)

    print(f"Finished {model_name}")


def get_handmade_conv():
    return [
        [
            "Show me all the text files on the Desktop",
            "Now move these files to the new folder \"Text_Data\"",
            "What is the IP address?",
            "Check whether the computer is connected to the internet",
        ],
        [
            "",
            "",
            "",
            "",
        ]
    ]


if __name__ == '__main__':
    available_models = [
        "gpt2_epoch_2",
        "gpt2_lora_epoch_2",
        "gpt2-medium_epoch_2",
        "gpt2-medium_lora_epoch_2",
        "gpt2-large_epoch_2",
        "gpt2-large_lora_epoch_2",
    ]

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    data = [get_handmade_conv()]

    stop_words_ids = [tokenizer(stop_word, return_tensors='pt')[
        'input_ids'].squeeze() for stop_word in Headers.all_headers]

    stopping_criteria = StoppingCriteriaList(
        [KeywordsStoppingCriteria(stops=stop_words_ids, device=DEVICE)])

    for model in available_models:
        evaluate(model, stopping_criteria, data)
