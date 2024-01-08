from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from units.string_matrix import to_string, to_matrix

from data.database.db import *
import data.config as config


async def main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="⛵️ Играть"),
    )
    builder.row(
        types.KeyboardButton(text="👤 Профиль"),
        types.KeyboardButton(text="🏆 Топ")
    )
    return builder.as_markup(resize_keyboard=True)


async def game_mode_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="👤 Против игрока", callback_data="play_with_player:0"),
        ],
        [
            types.InlineKeyboardButton(text="🤖 Против бота", callback_data="play_with_bot")
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def get_rooms_keyboard(page):
    rooms = await get_all_rooms()
    buttons = []
    items_per_page = 10
    start_index = page * items_per_page
    end_index = page * items_per_page + items_per_page
    page_items = rooms[start_index:end_index]
    has_next_page = end_index < len(rooms)
    for room in page_items:
        if room[2] == 0:
            buttons.append([types.InlineKeyboardButton(text=f"🔎 #{room[0]}", callback_data=f"join_room:{room[0]}:open")])
        elif room[2] == -1:
            buttons.append([types.InlineKeyboardButton(text=f"🔐 #{room[0]}", callback_data=f"join_room:{room[0]}:private")])
        else:
            buttons.append([types.InlineKeyboardButton(text=f"🔒 #{room[0]}", callback_data=f"join_room:{room[0]}:close")])
    if len(buttons) == 0:
        buttons.append([types.InlineKeyboardButton(text="Комнат не найдено", callback_data="no_rooms")])
    navigation_buttons = []
    if page != 0 and has_next_page:
        navigation_buttons.append(
            types.InlineKeyboardButton(text="⬅️", callback_data=f"play_with_player:{page - 1}"))
        navigation_buttons.append(
            types.InlineKeyboardButton(text="➡️", callback_data=f"play_with_player:{page + 1}"))
    elif page != 0:
        navigation_buttons.append(
            types.InlineKeyboardButton(text="⬅️", callback_data=f"play_with_player:{page - 1}"))
    elif has_next_page:
        navigation_buttons.append(
            types.InlineKeyboardButton(text="➡️", callback_data=f"play_with_player:{page + 1}"))
    navigation_buttons.append(types.InlineKeyboardButton(text="🔄", callback_data=f"play_with_player:{page}"))
    buttons.append(navigation_buttons)
    buttons.append([types.InlineKeyboardButton(text="✏️ Создать комнату", callback_data="select_create_room")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def room_type_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="🔐 Приватная", callback_data="create_room:private"),
        ],
        [
            types.InlineKeyboardButton(text="🔓 Публичная", callback_data="create_room:public")
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def set_field_keyboard(room_status):
    buttons = [
        [
            types.InlineKeyboardButton(text="🔄 Сгенирировать", callback_data=f"random_field:{room_status}")
        ],
        [
            types.InlineKeyboardButton(text="✅ Начать бой", callback_data=f"start_game:{room_status}")
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def settings_room_keyboard(room_id, user_id):
    buttons = [
        [
            types.InlineKeyboardButton(text="📣 Отправить приглашение", url=f"https://telegram.me/share/url?url=Привет! Я создал комнату в игре {config.bot_name}. Присоединяйся!\n\nt.me/{config.bot_username}?start={room_id}_{user_id}")
        ],
        [
            types.InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_room")
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def field_keyboard(str_field):
    field = to_matrix(str_field)
    all_buttons = []

    for i in range(6):
        buttons = []
        for j in range(6):
            if field[i][j] == '5':
                buttons.append(types.InlineKeyboardButton(text="🔥", callback_data=f"fire:{i}:{j}:no"))
            elif field[i][j] == '6':
                buttons.append(types.InlineKeyboardButton(text="❌", callback_data=f"fire:{i}:{j}:no"))
            elif field[i][j] == '7':
                buttons.append(types.InlineKeyboardButton(text="✖️", callback_data=f"fire:{i}:{j}:no"))
            else:
                buttons.append(types.InlineKeyboardButton(text=" ", callback_data=f"fire:{i}:{j}:yes"))
        all_buttons.append(buttons)
    all_buttons.append([types.InlineKeyboardButton(text="Закончить", callback_data=f"stop_game"), types.InlineKeyboardButton(text="Сдаться", callback_data=f"give_up")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=all_buttons)
    return keyboard


async def close_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="❌ Закрыть", callback_data="close")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard