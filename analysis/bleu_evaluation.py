import json
import os
import torch
from analysis.helpers import make_predictions
from core.helpers import reset_seeds
from training.train_data_loader import get_eval_dataset
from datasets import load_metric
from core.enums import Headers
from core.prompter import generate_prompt
from transformers import StoppingCriteriaList, GPT2Tokenizer
from generating.generate import KeywordsStoppingCriteria


DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
limit = 100


def evaluate(model_name: str, stopping_criteria: StoppingCriteriaList, data: list):
    predictions = make_predictions(
        model_name=model_name, stopping_criteria=stopping_criteria, data=data, limit=limit, device=DEVICE)

    path = os.path.join('bleu2', f'{model_name}_answers_data.json')
    with open(path, 'w') as f:
        json.dump(predictions, f)

    predicted = []
    references = []
    for conversation in predictions[:limit]:
        for _, pa in conversation:
            prediction, answer = pa
            predicted.append(prediction)
            references.append(answer)

    sacrebleu = load_metric('sacrebleu')
    # Compute the BLEU score
    score = sacrebleu.compute(predictions=predicted, references=references)
    # Output the score
    print("Model:", model_name, "BLEU Score:", score["score"])


if __name__ == '__main__':
    find_lrs = False
    train_models = True
    available_models = [
        "gpt2_epoch_2",
        "gpt2_lora_epoch_2",
        "gpt2-medium_epoch_2",
        "gpt2-medium_lora_epoch_2",
        "gpt2-large_epoch_2",
        "gpt2-large_lora_epoch_2",
    ]

    reset_seeds()
    dataset = get_eval_dataset()

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    data = []
    for conv in dataset['test']['conversation']:
        questions = []
        answers = []

        for idx, entry in enumerate(conv):
            if idx % 2 == 0:
                question = generate_prompt(conv[:(idx+1)], end_with_ai_token=True)
                
                encoded_question = tokenizer(question, return_tensors='pt')
                encoded_answer = tokenizer(conv[idx+1], return_tensors='pt')
                
                if len(encoded_question['input_ids'][0]) + len(encoded_answer['input_ids'][0]) > 1024:
                    break
                questions.append(conv[idx])
            else:
                answers.append(conv[idx])
        data.append([questions, answers])

    stop_words_ids = [tokenizer(stop_word, return_tensors='pt')[
        'input_ids'].squeeze() for stop_word in Headers.all_headers]

    stopping_criteria = StoppingCriteriaList(
        [KeywordsStoppingCriteria(stops=stop_words_ids, device=DEVICE)])

    for model in available_models:
        evaluate(model, stopping_criteria, data)
