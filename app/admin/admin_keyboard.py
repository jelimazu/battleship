from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

from data.database.db import *
import data.config as config


def admin_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"statistic"),
        ],
        [
            InlineKeyboardButton(text="📨 Рассылка", callback_data=f"send_mailing"),
        ],
        [
            InlineKeyboardButton(text="❌", callback_data=f"cancel")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def mailing_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="📨 Отправить", callback_data=f"count_send_mailing"),
            InlineKeyboardButton(text="🔄 Заново", callback_data=f"send_mailing")
        ],
        [
            InlineKeyboardButton(text="❌", callback_data=f"cancel")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def ask_mailing_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="📨 Отправить", callback_data=f"start_send_mailing")
        ],
        [
            InlineKeyboardButton(text="❌", callback_data=f"cancel")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def admin_cancel_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="❌", callback_data=f"cancel")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard