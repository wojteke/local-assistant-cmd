from core.enums import Headers


def generate_prompt(conversation: list[str], add_ai_token=False) -> str:
    conversation = list(_add_headers(conversation))
    prompt = [Headers.conversation+"\n\n"]
    for idx, entry in enumerate(conversation):
        entry += "\n\n"
        prompt.append(entry)
    result = "".join(prompt)
    if add_ai_token:
        result += Headers.ai + "\n"
    return result


def get_last_response(text: str, with_header=False) -> str:
    response = text.split(Headers.ai)[-1]
    if with_header:
        response = Headers.ai + response
    return response.strip()


def _add_headers(conversation: list[str]):
    for idx, entry in enumerate(conversation):
        if idx % 2 == 0:
            yield Headers.user + "\n" + entry
        else:
            yield Headers.ai + "\n" + entry
