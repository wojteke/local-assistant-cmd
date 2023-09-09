class Headers():
    conversation = "CONVERSATION:"
    user = "USER:"
    ai = "AI:"
    all_headers = [conversation, user, ai]


class GPT2Models(str):
    gpt2 = 'gpt2'
    gpt2_medium = 'gpt2-medium'
    gpt2_large = 'gpt2-large'
    gpt2_xl = 'gpt2-xl'