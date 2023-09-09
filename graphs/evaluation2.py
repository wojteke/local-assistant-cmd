import json
import os
import random
import numpy as np
import torch
from core.model_loader import load_gpt2_model
from core.enums import GPT2Models
from training.train_data_loader import get_eval_dataset
from datasets import DatasetDict, load_metric
from core.enums import Headers
from core.prompter import get_last_response, generate_prompt
from transformers import StoppingCriteriaList, GPT2Tokenizer
from tqdm import tqdm
from generating.generate import KeywordsStoppingCriteria


device = 'cuda' if torch.cuda.is_available() else 'cpu'
seed_val = 42
limit = 100


def evaluate(model_name: str, stopping_criteria: StoppingCriteriaList, data: list):
    tokenizer, model = load_gpt2_model(model_name)
    model = model.to(device)
    predictions = []
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)
    for questions, answers in tqdm(data[:limit]):
        pred_conv = []
        conv = []
        for question, answer in zip(questions, answers):
            quest = generate_prompt(conv + [question], True)
            encoded = tokenizer(quest, return_tensors='pt')
            if len(encoded['input_ids'][0]) >= 1024:
                break
            encoded = encoded.to(device)
            generation_output = model.generate(
                input_ids=encoded['input_ids'],
                attention_mask=encoded['attention_mask'],
                pad_token_id=tokenizer.pad_token_id,
                do_sample=True,
                temperature=1,
                top_k=50,
                # max_new_tokens below works better as shown in work
                #max_length=1024,
                max_new_tokens=min(200, 1024-len(encoded['input_ids'][0])),
                top_p=0.5,
                num_return_sequences=1,
                stopping_criteria=stopping_criteria
            )

            s = generation_output[0]
            output = tokenizer.decode(s, skip_special_tokens=True)
            output = output.removesuffix(Headers.user)
            conv.append(question)
            conv.append(get_last_response(output))
            pred_conv.append([quest, [get_last_response(output), [answer]]])
        predictions.append(pred_conv)

    path = os.path.join('bleu2', f'{model_name}_answers_data.json')
    with open(path, 'w') as f:
        json.dump(predictions, f)

    predicted = []
    references = []
    for conversation in predictions[:limit]:
        for question, pa in conversation:
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

    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)
    dataset = get_eval_dataset()

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    data = []
    for conversation in dataset['validation']["conversation"]:
        questions = []
        answers = []

        for idx, entry in enumerate(conversation):
            if idx % 2 == 0:
                question = generate_prompt(conversation[:(idx+1)], add_ai_token=True)
                encoded_question = tokenizer(question, return_tensors='pt')
                encoded_answer = tokenizer(conversation[idx+1], return_tensors='pt')
                if len(encoded_question['input_ids'][0]) + len(encoded_answer['input_ids'][0]) > 1024:
                    break
                questions.append(conversation[idx])
            else:
                answers.append(conversation[idx])
        data.append([questions, answers])


    stop_words_ids = [tokenizer(stop_word, return_tensors='pt')[
        'input_ids'].squeeze() for stop_word in Headers.all_headers]

    stopping_criteria = StoppingCriteriaList(
        [KeywordsStoppingCriteria(stops=stop_words_ids, device=device)])

    for model in available_models:
        evaluate(model, stopping_criteria, data)
