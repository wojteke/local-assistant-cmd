from tqdm import tqdm
from transformers import StoppingCriteriaList
from core.enums import Headers
from core.helpers import reset_seeds
from core.model_loader import load_gpt2_model
from core.prompter import generate_prompt, get_last_response


def make_predictions(model_name: str, stopping_criteria: StoppingCriteriaList, data: list, limit: int, device: str):
    tokenizer, model = load_gpt2_model(model_name)
    model = model.to(device)
    predictions = []
    reset_seeds()
    for questions, answers in tqdm(data[:limit]):
        pred_conv = []
        conv = []
        for question, answer in zip(questions, answers):
            prompt = generate_prompt(conv + [question], True)
            encoded = tokenizer(prompt, return_tensors='pt')
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
                # max_length=1024,
                # max_new_tokens below works better as shown in paper
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
            pred_conv.append([prompt, [get_last_response(output), [answer]]])
        predictions.append(pred_conv)
    return predictions
