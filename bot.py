import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from main import run, format_questions, save_settings, refresh_questions


# Чтение токена из файла
with open("bot_token.txt", "r", encoding="utf-8") as f:
    BOT_TOKEN = f.read().strip()

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# FSM состояния
class SetDifficulty(StatesGroup):
    easy = State()
    medium = State()
    hard = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать! Используйте /today, /refresh, /set, /solved или /set_session.")

@router.message(Command("today"))
async def cmd_today(message: Message):
    await message.answer("Выводим задачи на сегодня...")
    with open("Data/user_sessions.json", "r", encoding="utf-8") as f:
        sessions = json.load(f)
    session = sessions.get(str(message.from_user.id), None)
    questions = run(session, str(message.from_user.id))
    await message.answer(format_questions(questions))

@router.message(Command("refresh"))
async def cmd_refresh(message: Message):
    await message.answer("Обновляем файл с актуальными нерешёнными задачами...")
    with open("Data/user_sessions.json", "r", encoding="utf-8") as f:
        sessions = json.load(f)
    session = sessions.get(str(message.from_user.id), None)
    if not session:
        await message.answer("Сессия не найдена. Пожалуйста, установите сессию с помощью /set_session.")
        return
    count_not_solved, count_solved = refresh_questions(session, str(message.from_user.id))
    if count_not_solved > 0 or count_solved > 0:
        await message.answer(f"Обновлено. Получено {count_not_solved} нерешенных и {count_solved} решенных задач.")
    else:
        await message.answer("Не удалось обновить задачи. Проверьте сессию или запрос.")


@router.message(Command("set"))
async def cmd_set(message: Message, state: FSMContext):
    await message.answer("Сколько задач Easy вы хотите решать?")
    await state.set_state(SetDifficulty.easy)

@router.message(SetDifficulty.easy)
async def set_easy(message: Message, state: FSMContext):
    try:
        easy_count = int(message.text)
        await state.update_data(easy=easy_count)
        await message.answer("Сколько задач Medium вы хотите решать?")
        await state.set_state(SetDifficulty.medium)
    except ValueError:
        await message.answer("Введите число.")

@router.message(SetDifficulty.medium)
async def set_medium(message: Message, state: FSMContext):
    try:
        medium_count = int(message.text)
        await state.update_data(medium=medium_count)
        await message.answer("Сколько задач Hard вы хотите решать?")
        await state.set_state(SetDifficulty.hard)
    except ValueError:
        await message.answer("Введите число.")

@router.message(SetDifficulty.hard)
async def set_hard(message: Message, state: FSMContext):
    try:
        hard_count = int(message.text)
        await state.update_data(hard=hard_count)
        data = await state.get_data()
        settings = {
            "count_by_difficulty": {
                "Easy": data["easy"],
                "Medium": data["medium"],
                "Hard": data["hard"]
            }
        }
        user_id = str(message.from_user.id)
        save_settings(user_id, settings)
        await message.answer("Настройки сохранены. Проверь консоль!")
        await state.clear()
    except ValueError:
        await message.answer("Введите число.")
    print(f"Настройки сохранены: {settings}\n\n\n")

@router.message(Command("solved"))
async def cmd_solved(message: Message):
    """
    Выводит количество решенных задач по сложностям
    """
    try:
        with open("Data/solved_questions.json", "r", encoding="utf-8") as f:
            solved_questions = json.load(f)
        user_solved = solved_questions.get(str(message.from_user.id), [])
        easy_count = sum(1 for q in user_solved if q["difficulty"] == "Easy")
        medium_count = sum(1 for q in user_solved if q["difficulty"] == "Medium")
        hard_count = sum(1 for q in user_solved if q["difficulty"] == "Hard")
        await message.answer(
            f"Решено задач:\n"
            f"Easy: {easy_count}\n"
            f"Medium: {medium_count}\n"
            f"Hard: {hard_count}"
        )
    except FileNotFoundError:
        await message.answer("Файл с решенными задачами не найден. Выполните /refresh.")

class SetSession(StatesGroup):
    waiting_for_cookie = State()

@router.message(Command("set_session"))
async def cmd_set_session(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте ваш LEETCODE_SESSION:")
    await state.set_state(SetSession.waiting_for_cookie)

@router.message(SetSession.waiting_for_cookie)
async def process_session_cookie(message: Message, state: FSMContext):
    session = message.text.strip()
    user_id = str(message.from_user.id)

    try:
        with open("Data/user_sessions.json", "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except FileNotFoundError:
        sessions = {}

    sessions[user_id] = session

    print(f"Сессия для пользователя {user_id} сохранена: {session}")
    print(sessions)
    with open("Data/user_sessions.json", "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=4)

    await message.answer("Сессия сохранена.")
    await state.clear()


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Начать взаимодействие с ботом\n"
        "/today - Получить задачи на сегодня\n"
        "/refresh - Обновить список нерешенных задач\n"
        "/set - Настроить количество задач по сложности\n"
        "/solved - Показать количество решенных задач по сложностям\n"
        "/set_session - Установить LEETCODE_SESSION для работы с ботом\n" 
        "Примечание: Перед использованием бота, пожалуйста, установите LEETCODE_SESSION с помощью команды /set_session.\n"
        "/help - Показать это сообщение"
    )
    await message.answer(help_text)


async def main():
    print("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
