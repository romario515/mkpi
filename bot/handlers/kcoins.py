from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from emoji import emojize

database = None


class KCoinsManager(StatesGroup):
    waiting_for_group = State()
    waiting_for_action = State()
    waiting_for_count = State()
    waiting_for_confirm = State()


async def statistic_start(message: types.Message, state: FSMContext):
    if str(message.chat.id) in database.get_admin_list():
        kcoins_stat = database.get_all_groups()
        kcoins_stat_msg = 'Введите дату (пример: 27.10.2023)(в процессе разработки)\n'
        await message.answer(emojize(kcoins_stat_msg), reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.add("Возврат в меню")
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("В начало")
        await message.answer("У тебя здесь нет власти!",
                             reply_markup=keyboard)



# TODO




def register_handlers_statistic(dp: Dispatcher, db):
    global database
    database = db
    dp.register_message_handler(statistic_start, commands="statistic", state="*")
    dp.register_message_handler(statistic_start, Text(equals="Архив", ignore_case=True),
                                state="*")
