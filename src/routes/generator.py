import torch
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.schemas import TextRequest
from src.dependencies import get_model, get_tokenizer, get_db
from src.db import crud
import psycopg2
from typing import AsyncGenerator

router = APIRouter(prefix="/api/v1", tags=["api"])


# @router.post("/generate")
# async def generate_text(
#     request: TextRequest,
#     model: GPT2LMHeadModel = Depends(get_model),
#     tokenizer: GPT2Tokenizer = Depends(get_tokenizer),
#     db_conn: psycopg2.extensions.connection = Depends(get_db)
# ):
#     # If session_id is not provided or is None, create a new session
#     if request.session_id is None:
#         session_id = await crud.create_session(db_conn, "default_user")
#         history = []  # No history for a new session
#     else:
#         session_id = request.session_id

#         # Fetch session history
#         history = await crud.get_session_history(db_conn, session_id)
#         if not history and session_id != request.session_id:
#             raise HTTPException(status_code=404, detail="Session ID not found")

#     history_text = " ".join([msg["message"] for msg in history])

#     # Append the new message to the history
#     full_text = f"{history_text} {request.message}"

#     # Generate response
#     inputs = tokenizer.encode(full_text, return_tensors="pt")
#     with torch.no_grad():
#         outputs = model.generate(
#             inputs, max_new_tokens=100, num_return_sequences=1)
#         generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     # Save the new message and the response
#     await crud.add_message(db_conn, session_id, request.message)
#     await crud.add_message(db_conn, session_id, generated_text)

#     return {"session_id": session_id, "generated_text": generated_text}

async def generate_text_stream(model, tokenizer, input_text, max_new_tokens) -> AsyncGenerator[str, None]:
    inputs = tokenizer(input_text, return_tensors="pt")
    input_ids = inputs["input_ids"]

    # Generate response in chunks
    outputs = model.generate(
        input_ids,
        max_new_tokens=max_new_tokens,
        num_return_sequences=1,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        early_stopping=True
    )

    for token_id in outputs[0]:
        token = tokenizer.decode(token_id, skip_special_tokens=False)
        yield token

@router.post("/generate")
async def generate_text(
    request: TextRequest,
    model: AutoModelForCausalLM = Depends(get_model),
    tokenizer: AutoTokenizer = Depends(get_tokenizer),
    db_conn: psycopg2.extensions.connection = Depends(get_db)
):
    # If session_id is not provided or is None, create a new session
    if request.session_id is None:
        session_id = await crud.create_session(db_conn, "default_user")
        history = []  # No history for a new session
    else:
        session_id = request.session_id

        # Fetch session history
        history = await crud.get_session_history(db_conn, session_id)
        if not history and session_id != request.session_id:
            raise HTTPException(status_code=404, detail="Session ID not found")

    history_text = " ".join([msg["message"] for msg in history])

    # Append the new message to the history
    full_text = f"{history_text} {request.message}"

    # Save the new message
    await crud.add_message(db_conn, session_id, request.message)

    # Create a generator for the streaming response
    async def text_stream_generator() -> AsyncGenerator[str, None]:
        generated_text = ""
        async for token in generate_text_stream(model, tokenizer, full_text, 100):
            generated_text += token
            if token.strip():
                await crud.add_message(db_conn, session_id, token)
                yield generated_text
                generated_text = ""

    return StreamingResponse(text_stream_generator(), media_type="text/plain")