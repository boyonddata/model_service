from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.db import get_db_conn
from src.utils.log import log_info

model = None
tokenizer = None


# async def load_model():
#     global model, tokenizer
#     model_name = "gpt2"
#     tokenizer = GPT2Tokenizer.from_pretrained(model_name)
#     model = GPT2LMHeadModel.from_pretrained(model_name)
#     model.eval()

async def load_model():
    global model, tokenizer
    model_path = "/home/peter/bdata/source/modeldev/model"  # Path to the locally saved model
    tokenizer_path = "/home/peter/bdata/source/modeldev/model"  # Path to the locally saved tokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    model.eval()

def get_model():
    return model


def get_tokenizer():
    return tokenizer


def get_db():
    return next(get_db_conn())


def get_logger():
    def logger(message: str):
        log_info(message)

    return logger
