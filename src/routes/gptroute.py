import asyncio
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse
import openai
from pydantic import BaseModel
from src.schemas import TextRequest
from src.db import crud
from src.dependencies import get_db
import psycopg2
from openai import OpenAI
from src.settings import settings
from typing import AsyncGenerator

client = OpenAI(api_key=settings.api_key)

router = APIRouter(prefix="/api/v1", tags=["api"])

API_KEY_NAME = "api-key"
API_KEY_VALUE = "ce06e67c-d960-4b7b-98d7-9893d0cdb4f4"  

def get_api_key(api_key: str = Header(None)):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API key is missing")
    if api_key != API_KEY_VALUE:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@router.post("/generate_chatgpt")
async def generate_text_chatgpt(
    request: TextRequest,
    db_conn: psycopg2.extensions.connection = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    session_id = request.session_id
    if session_id is None:
        session_id = await crud.create_session(db_conn, "default_user")
        history = [{"role": "system", "content": settings.inital_prompt}]
    else:
        history = await crud.get_session_history(db_conn, session_id)
        if not history and session_id != request.session_id:
            raise HTTPException(status_code=404, detail="Session ID not found")

        formatted_history = [{"role": "system", "content": settings.inital_prompt}]
        for i, msg in enumerate(history):
            if 'message' in msg:
                role = "user" if i % 2 == 0 else "assistant"
                formatted_history.append({"role": role, "content": msg["message"]})
        history = formatted_history

    history.append({"role": "user", "content": request.message})

    response = client.chat.completions.create(model=settings.model_name,
                                              messages=history,
                                              max_tokens=150)
    ai_message = response.choices[0].message.content.strip()

    await crud.add_message(db_conn, session_id, request.message)
    await crud.add_message(db_conn, session_id, ai_message)

    return JSONResponse(content={"session_id": session_id, "generated_text": ai_message})

# @router.post("/generate_chatgpt")
# async def generate_text_chatgpt(
#     request: TextRequest,
#     db_conn: psycopg2.extensions.connection = Depends(get_db)
# ):

#     if request.session_id is None:
#         session_id = await crud.create_session(db_conn, "default_user")
#         history = [{"role": "system", "content": settings.inital_prompt}]
#     else:
#         session_id = request.session_id
#         history = await crud.get_session_history(db_conn, session_id)
#         if not history and session_id != request.session_id:
#             raise HTTPException(status_code=404, detail="Session ID not found")
#     messages = [{"role": "user", "content": msg["message"]} if i % 2 == 0 else {
#         "role": "assistant", "content": msg["message"]} for i, msg in enumerate(history)]
#     messages.append({"role": "user", "content": request.message})
#     response = client.chat.completions.create(model=settings.model_name,
#                                               messages=messages,
#                                               max_tokens=150)
#     ai_message = response.choices[0].message.content.strip()
#     await crud.add_message(db_conn, session_id, request.message)
#     await crud.add_message(db_conn, session_id, ai_message)
#     return JSONResponse(content={"session_id": session_id, "generated_text": ai_message})


# async def generate_text_stream(client, messages, model="gpt-3.5-turbo") -> AsyncGenerator[str, None]:
#     response = await asyncio.to_thread(
#         client.chat.completions.create,
#         model=model,
#         messages=messages,
#         stream=True
#     )

#     for chunk in response:
#         chunk_message = chunk.choices[0].delta.content if 'content' in chunk.choices[0].delta else ''
#         if chunk_message:
#             yield chunk_message

# @router.post("/generate_streamgpt")
# async def generate_text_streamgpt(
#     request: TextRequest,
#     db_conn: psycopg2.extensions.connection = Depends(get_db)
# ):
#     if request.session_id is None:
#         session_id = await crud.create_session(db_conn, "default_user")
#         history = []
#     else:
#         session_id = request.session_id
#         history = await crud.get_session_history(db_conn, session_id)
#         if not history and session_id != request.session_id:
#             raise HTTPException(status_code=404, detail="Session ID not found")

#     messages = [{"role": "user", "content": msg["message"]} if i % 2 == 0 else {
#         "role": "assistant", "content": msg["message"]} for i, msg in enumerate(history)]
#     messages.append({"role": "user", "content": request.message})

#     # Save the new user message in the database
#     await crud.add_message(db_conn, session_id, request.message)

#     # Create a generator for the streaming response
#     async def text_stream_generator() -> AsyncGenerator[str, None]:
#         async for token in generate_text_stream(client, messages, settings.model_name):
#             await crud.add_message(db_conn, session_id, token)
#             yield token

#     return StreamingResponse(text_stream_generator(), media_type="text/plain")