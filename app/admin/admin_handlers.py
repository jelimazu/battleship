from aiogram import Router, F, Bot
from aiogram.filters import ExceptionMessageFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from app.admin.admin_keyboard import *
from aiogram.handlers import ErrorHandler
import datetime
import emoji

from data.config import *
import data.config as config

router = Router()


class AdminState(StatesGroup):
    set_message = State()
    set_count = State()


@router.message(Command("admin"))
async def admin(message: Message):
    await message.answer("Вы вошли в админ панель", reply_markup=admin_keyboard())
    try:
        await message.delete()
    except:
        pass


@router.callback_query(F.data.startswith("statistic"))
async def statistic(call: CallbackQuery):
    await call.answer()
    dates = await db.get_all_reg_date()
    today = 0
    yesterday = 0
    weak = 0
    month = 0
    all_time = 0
    today_ = datetime.datetime.strptime(get_now_date(), "%d.%m.%Y")

    # Получить номер дня недели
    weekday = today_.weekday()

    # Вычесть номер дня недели из текущей даты
    start_of_week = today_ - datetime.timedelta(days=weekday)
    start_of_month = today_ - datetime.timedelta(days=month)
    for date in dates:
        if datetime.datetime.strptime(date[0], "%d.%m.%Y") == datetime.datetime.strptime(get_now_date(), "%d.%m.%Y"):
            today += 1
        if datetime.datetime.strptime(date[0], "%d.%m.%Y") == datetime.datetime.strptime(get_now_date(), "%d.%m.%Y") - datetime.timedelta(days=1):
            yesterday += 1
        if datetime.datetime.strptime(date[0], "%d.%m.%Y") >= start_of_week:
            weak += 1
        if datetime.datetime.strptime(date[0], "%d.%m.%Y") >= start_of_month:
            month += 1
        all_time += 1
    text = f"📊 <b>Статистика бота @{config.bot_username}</b>\n\n<b> └ Сегодня:</b> <i>{today}</i>\n<b> └ Вчера:</b> <i>{yesterday}</i>\n<b> └ С начала недели:</b> <i>{weak}</i>\n<b> └ С начала месяца:</b> <i>{month}</i>\n<b> └ За всё время:</b> <i>{all_time}</i>\n"
    await call.message.answer(text, parse_mode="HTML")

@router.callback_query(F.data.startswith("send_mailing"))
async def send_mailing(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите текст или фото рассылки", reply_markup=admin_cancel_keyboard())
    await state.set_state(AdminState.set_message)


@router.message(AdminState.set_message)
async def set_message(message: Message, state: FSMContext):
    if message.photo:
        if message.caption:
            text = message.caption
        else:
            text = ""
        await message.answer_photo(message.photo[-1].file_id, caption="Ваша рассылка:\n\n" + text, parse_mode="HTML", reply_markup=mailing_keyboard())
        await state.update_data(message=text, photo=message.photo[-1].file_id, type="photo")
    else:
        text = "Ваша рассылка:\n\n" + message.text
        await message.answer(text, reply_markup=mailing_keyboard())
        await state.update_data(message=message.text, type="text")


@router.callback_query(F.data.startswith("count_send_mailing"))
async def count_send_mailing(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите количество пользователей для рассылки\n\nЕсли хотите отправить всем, то введите <code>0</code>", parse_mode="HTML", reply_markup=admin_cancel_keyboard())
    await state.set_state(AdminState.set_count)


@router.message(AdminState.set_count, F.text)
async def set_count(message: Message, state: FSMContext):
    count = message.text
    if count.isdigit():
        if int(count) == 0:
            await message.answer("Вы уверены что хотите отправить всем пользователям?", reply_markup=ask_mailing_keyboard())
            await state.update_data(count=count)
        elif int(count) > 0:
            await message.answer("Вы уверены что хотите отправить рассылку?", reply_markup=ask_mailing_keyboard())
            await state.update_data(count=count)
        else:
            await message.answer("Вы ввели некорректное число")
    else:
        await message.answer("Вы ввели некорректное число")


@router.callback_query(F.data.startswith("start_send_mailing"))
async def start_send_mailing(call: CallbackQuery, state: FSMContext):
    await call.answer()
    users = await db.get_all_users_id()
    data = await state.get_data()
    message = data.get("message")
    type_ = data.get("type")
    count = int(data.get("count"))
    if type_ == "photo":
        photo = data.get("photo")
    await call.message.answer("Рассылка началась")
    success = 0
    failed = 0
    await state.clear()
    for user in users:
        try:
            if type_ == "text":
                await call.message.bot.send_message(user[0], message, parse_mode="HTML")
            elif type_ == "photo":
                await call.message.bot.send_photo(user[0], photo=photo, caption=message, parse_mode="HTML")
            await asyncio.sleep(0.05)
            success += 1
        except:
            failed += 1
        if success == count:
            break
    await call.message.answer(f"Рассылка закончилась\n\n<b>Успешно:</b> {success}\n<b>Не успешно:</b> {failed}", parse_mode="HTML")


@router.callback_query(F.data.startswith("cancel"))
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    try:
        await call.message.delete()
    except:
        pass


