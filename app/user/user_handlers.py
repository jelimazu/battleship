from aiogram import Router, F, Bot
from aiogram.filters import ExceptionMessageFilter, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.handlers import ErrorHandler
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, InputFile, BufferedInputFile
from random import randint

from app.user.user_keyboard import *
from data.database.db import *
from units.drawer import draw_field
from units.string_matrix import to_string, to_matrix
from units.number_player import get_number_player
from units.check_field import check_field
from fields import fields

router = Router()


@router.message(Command("start"))
async def start(message: Message, command: CommandObject, state: FSMContext):
    if not await get_user_exists(message.from_user.id):
        await add_user(message.from_user.id, message.from_user.first_name)
    if command.args:
        game = command.args
    else:
        game = None
    if game:
        info = game.split("_")
        if info[0].isdigit() and info[1].isdigit():
            room_id = int(info[0])
            user_id_1 = int(info[1])
            # Пока я писал этот промежуток кода, я пил квас и слушал музыку, поэтому не судите строго
            room = await get_room(room_id)
            if room[1] == user_id_1 and room[1] != message.chat.id:
                if room[2] == 1 or room[2] == 0:
                    if not await get_user_in_room(message.chat.id):
                        str_field = fields[randint(0, len(fields) - 1)]
                        field = to_matrix(str_field)
                        await state.update_data(field=field, room_id=room_id)
                        img_field = await draw_field(field)
                        img = BufferedInputFile(img_field, filename="img.png")
                        await message.answer_photo(photo=img, caption="Пожалуйста, выберите расстановку",
                                                   reply_markup=await set_field_keyboard("connect"))
                    else:
                        await message.answer("Вы уже находитесь в комнате")
                else:
                    await message.answer("Комната уже заполнена")
            else:
                await message.answer("Вы не можете подключиться к этой комнате")
        else:
            await message.answer("Комната не найдена")
    else:
        await message.answer("Добро пожаловать в бота для игры в морской бой!", reply_markup=await main_keyboard())


@router.message(F.text == "⛵️ Играть")
async def play(message: Message):
    await message.delete()
    await message.answer("Выберите режим игры", reply_markup=await game_mode_keyboard())


@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    await message.delete()
    user_info = await get_user(message.from_user.id)
    await message.answer(f"""👤 <b>Профиль</b>
    
🆔 ID: <code>{user_info[0]}</code>
📅 Дата регистрации: <b>{user_info[2]}</b>
🏆 Рейтинг: <b>{user_info[3]} очков</b>""", parse_mode="HTML")


@router.message(F.text == "🏆 Топ")
async def top(message: Message):
    await message.delete()
    top_10 = await get_top_10()
    text = "🏆 <b>Топ 10 игроков</b>\n\n"
    for user in top_10:
        text += f"<b>{user[1]}</b> - <b>{user[3]}</b> очков\n"
    await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data.startswith("play_with_bot"))
async def play_with_bot(call: CallbackQuery, state: FSMContext):
    await call.answer("Данная функция пока не доступна", show_alert=True)
    # Не знаю, как это реализовать, поэтому как-то так


@router.callback_query(F.data.startswith("play_with_player"))
async def play_with_player(call: CallbackQuery):
    info = call.data.split(":")
    page = int(info[1])
    try:
        await call.message.edit_text("Список комнат", reply_markup=await get_rooms_keyboard(page))
    except:
        await call.answer("Список комнат не изменился")


@router.callback_query(F.data.startswith("join_room"))
async def join_room(call: CallbackQuery, state: FSMContext):
    info = call.data.split(":")
    room_id = int(info[1])
    status = info[2]
    if status == "open":
        room = await get_room(room_id)
        if room[2] == 0:
            if not await get_user_in_room(call.message.chat.id):
                str_field = fields[randint(0, len(fields) - 1)]
                field = to_matrix(str_field)
                await state.update_data(field=field, room_id=room_id)
                img_field = await draw_field(field)
                img = BufferedInputFile(img_field, filename="img.png")
                await call.message.answer_photo(photo=img, caption="Пожалуйста, выберите расстановку",
                                                reply_markup=await set_field_keyboard("connect"))
                try:
                    await call.message.delete()
                except:
                    pass
            else:
                await call.answer("Вы уже находитесь в комнате", show_alert=True)
    elif status == "private":
        await call.answer("Вы не можете подключиться в приватную комнату", show_alert=True)
    elif status == "close":
        await call.answer("Комната закрыта", show_alert=True)


@router.callback_query(F.data == "select_create_room")
async def select_create_room(call: CallbackQuery):
    await call.message.edit_text("Выберите тип комнаты", reply_markup=await room_type_keyboard())


@router.callback_query(F.data.startswith("create_room"))
async def create_room(call: CallbackQuery, state: FSMContext):
    info = call.data.split(":")
    room_type = info[1]
    if not await get_user_in_room(call.message.chat.id):
        str_field = fields[randint(0, len(fields) - 1)]
        field = to_matrix(str_field)
        await state.update_data(field=field)
        img_field = await draw_field(field)
        img = BufferedInputFile(img_field, filename="img.png")
        await call.message.answer_photo(photo=img, caption="Пожалуйста, выберите расстановку",
                                        reply_markup=await set_field_keyboard(room_type))
        try:
            await call.message.delete()
        except:
            pass
    else:
        await call.answer("Вы уже находитесь в комнате", show_alert=True)


@router.callback_query(F.data.startswith("random_field"))
async def random_field(call: CallbackQuery, state: FSMContext):
    info = call.data.split(":")
    room_type = info[1]
    str_field = fields[randint(0, len(fields) - 1)]
    field = to_matrix(str_field)
    await state.update_data(field=field)
    img_field = await draw_field(field)
    img = BufferedInputFile(img_field, filename="img.png")
    await call.message.edit_media(media=InputMediaPhoto(media=img), reply_markup=await set_field_keyboard(room_type))
    await call.message.edit_caption(caption="Пожалуйста, выберите расстановку",
                                    reply_markup=await set_field_keyboard(room_type))


@router.callback_query(F.data.startswith("start_game"))
async def start_game(call: CallbackQuery, state: FSMContext):
    if not await get_user_in_room(call.message.chat.id):
        info = call.data.split(":")
        room_type = info[1]
        data = await state.get_data()
        field = data['field']
        await state.clear()
        m_id = call.message.message_id
        if room_type == "public" or room_type == "private":
            room_id = await create_new_room(room_type, call.message.chat.id, to_string(field), m_id,
                                            call.message.chat.first_name)
            await call.message.edit_caption(caption="Комната создана\n\nОжидаем соперника",
                                            reply_markup=await settings_room_keyboard(room_id, call.message.chat.id))
        elif room_type == "connect":
            room_id = data['room_id']
            room = await get_room(room_id)
            if room[2] == 0 or room[2] == 1:
                await add_user_to_room(room_id, call.message.chat.id, to_string(field), m_id,
                                       call.message.chat.first_name)
                await call.message.edit_caption(caption=f"Противник: {room[9]}\n\nОжидаем ход соперника",
                                                reply_markup=await field_keyboard(room[5]))
                await call.bot.edit_message_caption(chat_id=room[1], message_id=room[3],
                                                    caption=f"Противник: {call.message.chat.first_name}\n\nВаш ход:",
                                                    reply_markup=await field_keyboard(field))
            else:
                await call.answer("Комната уже заполнена", show_alert=True)
    else:
        await call.answer("Вы уже находитесь в комнате", show_alert=True)


@router.callback_query(F.data.startswith("fire"))
async def fire(call: CallbackQuery):
    info = call.data.split(":")
    x = int(info[1])
    y = int(info[2])
    status = info[3]
    # Тут ваще жара щас будет и это не шутка, я писал это трезвый в час ночи
    if status == "yes":
        game = await get_room_by_user_id(call.message.chat.id)
        if game:
            number_player = get_number_player(call.message.chat.id, game)
            field = to_matrix(game[7 - number_player])
            if number_player == game[7]:
                # Если клетка пустая
                if field[x][y] == "0":
                    field[x][y] = "7"
                    str_field = to_string(field)
                    await update_field_and_current_move(game[0], str_field, number_player)
                    img_field = await draw_field(field)
                    img = BufferedInputFile(img_field, filename="img.png")
                    await call.bot.edit_message_media(chat_id=game[3 - number_player],
                                                      message_id=game[5 - number_player],
                                                      media=InputMediaPhoto(media=img),
                                                      reply_markup=await field_keyboard(game[4 + number_player]))
                    await call.bot.edit_message_caption(chat_id=game[3 - number_player],
                                                        message_id=game[5 - number_player],
                                                        caption=f"Противник: {call.message.chat.first_name}\n\nВаш ход:",
                                                        reply_markup=await field_keyboard(game[4 + number_player]))
                    await call.message.edit_caption(
                        caption=f"Противник: {game[11 - number_player]}\n\nОжидаем ход соперника",
                        reply_markup=await field_keyboard(str_field))
                # Если клетка с кораблем
                else:
                    current = field[x][y]
                    same_cells_count = 0
                    for i in range(6):
                        for j in range(6):
                            if field[i][j] == current:
                                same_cells_count += 1
                    # Если клетка это не последняя клетка корабля
                    if same_cells_count > 1:
                        field[x][y] = "5"
                        str_field = to_string(field)
                        await update_field_without_move(game[0], str_field, number_player)
                        img_field = await draw_field(field)
                        img = BufferedInputFile(img_field, filename="img.png")
                        await call.bot.edit_message_media(chat_id=game[3 - number_player],
                                                          message_id=game[5 - number_player],
                                                          media=InputMediaPhoto(media=img),
                                                          reply_markup=await field_keyboard(game[4 + number_player]))
                        await call.bot.edit_message_caption(chat_id=game[3 - number_player],
                                                            message_id=game[5 - number_player],
                                                            caption=f"Противник: {call.message.chat.first_name}\n\nОжидаем ход соперника",
                                                            reply_markup=await field_keyboard(game[4 + number_player]))
                        await call.message.edit_caption(caption=f"Противник: {game[11 - number_player]}\n\nВаш ход:",
                                                        reply_markup=await field_keyboard(str_field))
                    # Если клетка последняя клетка корабля
                    else:
                        field[x][y] = "6"
                        x_, y_ = x, y
                        same_hit_cells = [[x_, y_]]
                        # Ищем соседние подбитые клетки и помечаем их как уничтоженные
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                if 0 <= x_ + i < 6 and 0 <= y_ + j < 6:
                                    if field[x_ + i][y_ + j] == "5":
                                        field[x_ + i][y_ + j] = "6"
                                        x_, y_ = x_ + i, y_ + j
                                        same_hit_cells.append([x_, y_])
                                        for _ in range(int(current) - 1):
                                            if 0 <= x_ + i < 6 and 0 <= y_ + j < 6:
                                                if field[x_ + i][y_ + j] == "5":
                                                    field[x_ + i][y_ + j] = "6"
                                                    x_, y_ = x_ + i, y_ + j
                                                    same_hit_cells.append([x_, y_])
                        # Проверяем, есть ли еще живые корабли
                        if check_field(field):
                            # Если есть, то помечаем клетки вокруг уничтоженного корабля как промахнутые
                            for cell in same_hit_cells:
                                for i in range(-1, 2):
                                    for j in range(-1, 2):
                                        if 0 <= cell[0] + i < 6 and 0 <= cell[1] + j < 6:
                                            if field[cell[0] + i][cell[1] + j] == "0":
                                                field[cell[0] + i][cell[1] + j] = "7"
                            str_field = to_string(field)
                            await update_field_without_move(game[0], str_field, number_player)
                            img_field = await draw_field(field)
                            img = BufferedInputFile(img_field, filename="img.png")
                            await call.bot.edit_message_media(chat_id=game[3 - number_player],
                                                              message_id=game[5 - number_player],
                                                              media=InputMediaPhoto(media=img),
                                                              reply_markup=await field_keyboard(game[
                                                                  4 + number_player]))
                            await call.bot.edit_message_caption(chat_id=game[3 - number_player],
                                                                message_id=game[5 - number_player],
                                                                caption=f"Противник: {call.message.chat.first_name}\n\nОжидаем ход соперника",
                                                                reply_markup=await field_keyboard(game[
                                                                    4 + number_player]))
                            await call.message.edit_caption(
                                caption=f"Противник: {game[11 - number_player]}\n\nВаш ход:",
                                reply_markup=await field_keyboard(str_field))
                        # Если нет, то игрок победил
                        else:
                            str_field = to_string(field)
                            await update_field_without_move(game[0], str_field, number_player)
                            img_field = await draw_field(field)
                            img = BufferedInputFile(img_field, filename="img.png")
                            await call.bot.edit_message_media(chat_id=game[3 - number_player],
                                                              message_id=game[5 - number_player],
                                                              media=InputMediaPhoto(media=img),
                                                              reply_markup=await field_keyboard(game[
                                                                  4 + number_player]))
                            await call.bot.edit_message_caption(chat_id=game[3 - number_player],
                                                                message_id=game[5 - number_player],
                                                                caption=f"Противник: {call.message.chat.first_name}\n\nВы проиграли :(",
                                                                reply_markup=await close_keyboard())
                            await call.message.edit_caption(
                                caption=f"Противник: {game[11 - number_player]}\n\nВы победили!",
                                reply_markup=await close_keyboard())
                            await delete_room(game[0])
                            await update_users_rating(call.from_user.id, game[3 - number_player])
            else:
                await call.answer("Сейчас не ваш ход", show_alert=True)
        else:
            await call.answer("Вы не находитесь в игре", show_alert=True)
    else:
        await call.answer("Данная клетка уже открыта", show_alert=True)


@router.callback_query(F.data == "stop_game")
async def stop_game(call: CallbackQuery):
    room = await get_room_by_user_id(call.message.chat.id)
    if room:
        number_player = get_number_player(call.message.chat.id, room)
        if number_player == room[7]:
            await call.answer("Вы не можете закончить игру, так как сейчас ваш ход", show_alert=True)
        else:
            if datetime.datetime.strptime(room[8], "%d.%m.%Y %H:%M") + datetime.timedelta(
                    minutes=5) < datetime.datetime.strptime(get_now_time(), "%d.%m.%Y %H:%M"):
                await call.message.edit_caption(caption=f"Противник: {room[11 - number_player]}\n\nВы победили!",
                                                reply_markup=await close_keyboard())
                await call.bot.edit_message_caption(chat_id=room[3 - number_player], message_id=room[5 - number_player],
                                                    caption=f"Противник: {call.message.chat.first_name}\n\nВы были слишком долго афк и проиграли :(",
                                                    reply_markup=await close_keyboard())
                await delete_room(room[0])
                await update_users_rating(call.from_user.id, room[3 - number_player])
            else:
                await call.answer(
                    "Вы не можете закончить игру, так как последний ход противника был совершен менее 5 минут назад",
                    show_alert=True)
    else:
        await call.answer("Вы не находитесь в комнате", show_alert=True)


@router.callback_query(F.data == "give_up")
async def give_up(call: CallbackQuery):
    room = await get_room_by_user_id(call.message.chat.id)
    if room:
        number_player = get_number_player(call.message.chat.id, room)
        await call.message.edit_caption(caption=f"Противник: {room[11 - number_player]}\n\nВы сдались :(",
                                        reply_markup=await close_keyboard())
        await call.bot.edit_message_caption(chat_id=room[3 - number_player], message_id=room[5 - number_player],
                                            caption=f"Противник: {call.message.chat.first_name}\n\nВы победили, противник сдался!",
                                            reply_markup=await close_keyboard())
        await delete_room(room[0])
        await update_users_rating(room[3 - number_player], call.from_user.id)
    else:
        await call.answer("Вы не находитесь в комнате", show_alert=True)


@router.callback_query(F.data == "cancel_room")
async def cancel_room(call: CallbackQuery):
    room = await get_room_by_user_id(call.message.chat.id)
    if room:
        await delete_room(room[0])
        try:
            await call.message.delete()
        except:
            pass
        await call.message.answer("Комната удалена")
    else:
        await call.answer("Вы не находитесь в комнате", show_alert=True)


@router.callback_query(F.data == "close")
async def close(call: CallbackQuery):
    await call.message.delete()


# Ловим ошибки
@router.errors(ExceptionMessageFilter(
    "Telegram server says - Bad Request: message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message")
)
class MyHandler(ErrorHandler):
    async def handle(self):
        pass


@router.error()
class MyHandler(ErrorHandler):
    async def handle(self):
        # Когда писал это, то квас, к сожалению, закончился
        print(self.exception_name)
        print(self.exception_message[self.exception_message.find("exception="):])
        config.logger.error(self.exception_name + " | " + self.exception_message[self.exception_message.find("exception="):])