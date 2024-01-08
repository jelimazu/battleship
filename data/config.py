import asyncio
import configparser
import datetime

import emoji
from aiogram.types import User

import data.database.db as db
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs.txt')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

config = configparser.ConfigParser()
config.read('settings.ini', encoding='utf-8')
data = config["settings"]
token = data["token"]
admin_id = list(map(int, data["admin_id"].split(",")))
bot_username = str
bot_name = str


async def update_data(user: User):
    global bot_username
    global bot_name

    bot_username = user.username
    bot_name = user.first_name
    print(f"@{bot_username}", bot_name)

