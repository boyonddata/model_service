from fastapi import FastAPI
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from src.routes import generator, gptroute
from src.dependencies import load_model
from src.db import init_db_pool, close_db_pool

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    init_db_pool()
    #await load_model()


@app.on_event("shutdown")
async def shutdown_event():
    close_db_pool()

#app.include_router(generator.router)
app.include_router(gptroute.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
