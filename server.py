from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import torch
from core.enums import Headers
from core.model_loader import load_gpt2_model
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from generating.generate import KeywordsStoppingCriteria, get_response, get_response_stream

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model_name = ""
tokenizer: GPT2Tokenizer = None
model: GPT2LMHeadModel = None
stopping_criteria: KeywordsStoppingCriteria = None

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

available_models = [
    "gpt2_cmd",
    "gpt2_lora_cmd",
    "gpt2-medium_cmd",
    "gpt2-medium_lora_cmd",
]


def get_model_path(model_name):
    return model_name.replace("_cmd", "_epoch_2")


def create_model(model_n):
    global tokenizer, model, model_name, stopping_criteria
    if model_name != model_n:
        tokenizer, model = load_gpt2_model(get_model_path(model_n))
        model.eval()
        model.to(DEVICE)
        stop_words_ids = [tokenizer(stop_word, return_tensors='pt')[
            'input_ids'].squeeze() for stop_word in Headers.all_headers]
        stopping_criteria = KeywordsStoppingCriteria(stops=stop_words_ids)

        model_name = model_n


class ChatDataDto(BaseModel):
    temperature: float
    top_p: float
    top_k: int
    model_name: str
    max_new_tokens: int
    conversation: list[str]


async def fake_video_streamer():
    for i in range(5):
        await asyncio.sleep(2)
        yield b"some fake video bytes"


@app.post("/api/ai-response")
async def ai_response(chat_data: ChatDataDto):
    create_model(chat_data.model_name)
    return Response(get_response(model=model,
                                 tokenizer=tokenizer,
                                 stopping_criteria=stopping_criteria,
                                 conversation=chat_data.conversation,
                                 temperature=chat_data.temperature,
                                 top_p=chat_data.top_p,
                                 top_k=chat_data.top_k,
                                 max_new_tokens=chat_data.max_new_tokens), media_type='text/plain')


@app.post("/api/stream/ai-response")
async def ai_reponse_stream(chat_data: ChatDataDto):
    create_model(chat_data.model_name)
    return StreamingResponse(get_response_stream(model=model,
                                                 tokenizer=tokenizer,
                                                 stopping_criteria=stopping_criteria,
                                                 conversation=chat_data.conversation,
                                                 temperature=chat_data.temperature,
                                                 top_p=chat_data.top_p,
                                                 top_k=chat_data.top_k,
                                                 max_new_tokens=chat_data.max_new_tokens), media_type='text/event-stream')


@app.post("/api/stream/video")
async def get_video_stream():
    return StreamingResponse(fake_video_streamer(), media_type='text/event-stream')


@app.post("/api/video")
async def get_video():
    data = []
    async for entry in fake_video_streamer():
        data.append(entry)
    return Response(data, media_type='text/plain')

if __name__ == "__main__":
    # create_model(available_models[0])

    # Start the API server
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
