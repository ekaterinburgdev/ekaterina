import os
from tokens import TOKEN_TG_LAMA, TOKEN_OpenIA
import logging
import sys
from llama_index import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from langchain import OpenAI
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatActions
import csv
import openai
import time

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

START_MSG = "Привет! Я - Екатерина, твой помощник в Екатеринбурге. Задавай вопросы!"
user_q_dict = {}
async_counter = 0

os.environ['OPENAI_API_KEY'] = TOKEN_OpenIA
OpenAI.api_key = TOKEN_OpenIA
openai.api_key = TOKEN_OpenIA
# documents = SimpleDirectoryReader('./data').load_data()  # read directory
# index = VectorStoreIndex.from_documents(documents)  # making index from documents
# index.storage_context.persist(persist_dir="<persist_dir>")  # saving index
storage_context = StorageContext.from_defaults(persist_dir="<persist_dir>")
index = load_index_from_storage(storage_context)  # already done index, just take


def ask_ai(msg, id_user):
    if user_q_dict.get(id_user) is not None:
        q_engine = user_q_dict[id_user]
    else:
        q_engine = index.as_query_engine()
        user_q_dict[id_user] = q_engine

    response = q_engine.query(msg)

    return response


def save_time_to_csv(counter, t):
    with open('logs.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([counter, t, t/counter])


bot = Bot(token=TOKEN_TG_LAMA)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(START_MSG)


@dp.message_handler()
async def start_handler(message: types.Message):
    global async_counter
    async_counter += 1

  
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    start = time.time()
    ans = ask_ai(message.text, message.from_id).response
    end = time.time()

  
    save_time_to_csv(async_counter, end - start)
    async_counter -= 1
    await message.reply(ans)


if __name__ == "__main__":
    executor.start_polling(dp)
