import logging
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from dotenv import load_dotenv
import os
import asyncio
from aiogram.types import FSInputFile, WebAppInfo
import re
import time


# Загрузка конфигурации
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Загрузка переводов
with open(Path(__file__).parent / 'translations.json', 'r', encoding='utf-8') as f:
    TRANSLATIONS = json.load(f)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Конфигурация
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1003005253453"))  # ID канала для проверки подписки
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/tradingaimoney")  # ссылка на канал для кнопки "Подписаться"
P_LINK = os.getenv("REG_LINK", "https://u3.shortink.io/register?utm_campaign=827062&utm_source=affiliate&utm_medium=sr&a=TkjGqov32uoKgx&ac=ai_trading_bot&sub_id2=us1&sub_id1=")
VIDEO_PATH = Path(__file__).parent / "intro.mp4"
BOT_DESCRIPTION = "Pocket Option AI Bot\nmade by maboy team"
USERS_FILE = Path(__file__).parent / 'users.json'
IMAGE_PATH = Path(__file__).parent / "assets/main_menu.jpg"

current_signal = {"trend": None, "time": None, "expires": 0}

# Настройки языков
LANGUAGES = {
    "ru": {"name": "Русский", "flag": "🇷🇺"},
    "en": {"name": "English", "flag": "🇬🇧"},
    "hi": {"name": "हिन्दी", "flag": "🇮🇳"},
    "id": {"name": "Bahasa", "flag": "🇮🇩"},
    "pt": {"name": "Português", "flag": "🇧🇷"},
    "vi": {"name": "Tiếng Việt", "flag": "🇻🇳"},
    "uk": {"name": "Українська", "flag": "🇺🇦"},
    "fr": {"name": "Français", "flag": "🇫🇷"}
}

# Хранилище данных пользователя
user_data = {}

def generate_signal():
    trend = random.choice(["Лонг", "Шорт"])
    minutes = random.randint(1, 20)
    expires = time.time() + minutes * 60  # истечёт через N минут
    return {"trend": trend, "time": minutes, "expires": expires}

async def show_main_menu(chat_id: int, lang: str = "en", message_id: int = None):
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    try:
        # проверка депозита и роли остаются как есть ...

        builder = ReplyKeyboardBuilder()
        builder.row(
            types.KeyboardButton(text=translations.get("reg", "📝 Registration")),
            types.KeyboardButton(text=translations.get("instr", "📚 Instructions"))
        )
        builder.row(types.KeyboardButton(text=translations.get("support", "🛠 Support")))
        builder.row(types.KeyboardButton(text="🚀 Get a signal"))

        if message_id:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)

        sent_message = await bot.send_video(
            chat_id=chat_id,
            video=FSInputFile(VIDEO_PATH),
            caption=f"<b>{translations.get('menu', 'Main Menu')}</b>",
            parse_mode="HTML",
            reply_markup=builder.as_markup(
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        return sent_message.message_id
    except Exception as e:
        logging.error(f"Error showing menu: {e}")

        builder = ReplyKeyboardBuilder()
        builder.row(
            types.KeyboardButton(text=translations.get("reg", "📝 Registration")),
            types.KeyboardButton(text=translations.get("instr", "📚 Instructions"))
        )
        builder.row(types.KeyboardButton(text=translations.get("support", "🛠 Support")))
        builder.row(types.KeyboardButton(text="🚀 Get a signal"))

        if message_id:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)

        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=f"<b>{translations.get('menu', 'Main Menu')}</b>",
            parse_mode="HTML",
            reply_markup=builder.as_markup(
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        return sent_message.message_id


async def show_registration(chat_id: int, lang: str = "en", message_id: int = None, user_id: int = None):
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    
    # Формируем персонализированную ссылку с ID пользователя
    personalized_link = f"{P_LINK}{user_id}"
    # Заменяем PERSONAL_LINK в сообщении на персонализированную ссылку
    registration_message = translations.get("registration_message", "Registration message").replace("PERSONAL_LINK", personalized_link)
    
    try:
        photo = FSInputFile(IMAGE_PATH)
        builder = ReplyKeyboardBuilder()
        
        builder.row(types.KeyboardButton(text=translations.get("next", "➡️ Next")))
        builder.row(types.KeyboardButton(text=translations.get("back", "⬅️ Back")))
        
        if message_id:
              # Задержка 2 секунды
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            
        sent_message = await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=registration_message,
            parse_mode="HTML",
            reply_markup=builder.as_markup(
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        return sent_message.message_id
    except Exception as e:
        logging.error(f"Error showing registration: {e}")
        builder = ReplyKeyboardBuilder()
        builder.row(types.KeyboardButton(text=translations.get("next", "➡️ Next")))
        builder.row(types.KeyboardButton(text=translations.get("back", "⬅️ Back")))
        
        if message_id:
              # Задержка 2 секунды
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
            
        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=registration_message,
            parse_mode="HTML",
            reply_markup=builder.as_markup(
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
        return sent_message.message_id

@dp.message(lambda m: m.text in [TRANSLATIONS[lang]["next"] for lang in LANGUAGES])
async def handle_send_id_entry(message: types.Message):
    uid = message.from_user.id
    lang = user_data.get(uid, {}).get("lang", "ru")
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    user_data.setdefault(uid, {})["last_stage"] = "awaiting_external_id"

    await message.answer(
        t.get("ask_external_id", "Пришлите ваш ID одним сообщением (только цифры).")
    )

    # ↓↓↓ вставка с отправкой фото ↓↓↓
    try:
        help_path = (Path(__file__).parent / "assets" / "help.jpg").resolve()
        if help_path.exists():
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=FSInputFile(str(help_path)),
                caption="Где найти ваш ID — пример на скриншоте."
            )
        else:
            logging.warning("Help image not found: %s", help_path)
    except Exception:
        logging.exception("send help.jpg failed")


async def notify_admins_about_confirmation(user_id: int):
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        me = next((u for u in data.get("users", []) if u["id"] == user_id), None)
        if not me:
            return

        note = (
            "Новая заявка на подтверждение:\n"
            f"external_id: {me.get('external_id')}\n"
            f"tg_id: {me['id']}\n"
            f"name: {me.get('name','')}\n"
            f"@{me.get('username','')}\n\n"
            f"Команды: /confirmation и /confirm {me.get('external_id')}"
        )

        admins = [u for u in data.get("users", []) if u.get("admin")]
        for a in admins:
            try:
                await bot.send_message(a["id"], note)
            except Exception:
                pass
    except Exception:
        logging.exception("notify_admins_about_confirmation failed")



######### UTIL 
def fmt_user_line(u: dict, idx: int) -> str:
    uname = f"@{u.get('username')}" if u.get("username") else "(no username)"
    name = u.get("name", "")
    return f"{idx}. external_id={u.get('external_id','')} | tg_id={u.get('id')} | {name} | {uname}"


def is_admin(user_id: int) -> bool:
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return any(u.get("id") == user_id and u.get("admin") for u in data.get("users", []))
    except Exception:
        logging.exception("is_admin failed")
        return False


def register_user_if_new(user):
    """
    Создаёт запись о пользователе, если её ещё нет.
    Без побочных эффектов, если пользователь уже есть.
    """
    try:
        # читаем текущее состояние
        data = {"users": []}
        if USERS_FILE.exists() and USERS_FILE.stat().st_size > 0:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        # уже есть?
        for u in data.get("users", []):
            if u.get("id") == user.id:
                return False  # уже зарегистрирован (ничего не меняем)
        # добавляем
        data.setdefault("users", []).append({
            "id": user.id,
            "name": user.full_name,
            "username": user.username or "",
            "reg": False,        # станет True после /confirm админом
            "confirm": False,    # True после отправки внешнего ID
            "external_id": "",   # внешний числовой ID
            "admin": False,      # админов назначаешь вручную
            "amount": 0,
            "dep":False
        })
        # сохраняем
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        logging.exception("register_user_if_new failed")
        return False


#######################################################################

@dp.message(Command("confirmation"))
async def cmd_confirmation(message: types.Message):
    uid = message.from_user.id
    if not is_admin(uid):
        # тихо игнорируем или отвечаем сообщением — на твой выбор
        await message.answer("Недостаточно прав.")
        return

    # загружаем пользователей и фильтруем ожидающих подтверждения
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        pending = [u for u in data.get("users", []) if u.get("confirm") and not u.get("reg")]
    except Exception:
        logging.exception("/confirmation read users failed")
        await message.answer("Ошибка чтения базы пользователей.")
        return

    if not pending:
        await message.answer("Нет заявок на подтверждение.")
        return

    # Сортируем: сначала те, у кого заполнен external_id, затем по времени (если есть), иначе как есть
    # (если у тебя есть timestamp — можешь заменить сортировку)
    pending_sorted = sorted(pending, key=lambda u: (u.get("external_id") is None, ))

    # бьём список пачками, чтобы не упереться в лимиты Telegram
    CHUNK = 20
    total = len(pending_sorted)
    header = f"Заявки на подтверждение ({total}):"

    await message.answer(header)
    block = []
    for i, u in enumerate(pending_sorted, start=1):
        block.append(fmt_user_line(u, i))
        if len(block) == CHUNK:
            await message.answer("\n".join(block))
            block = []
    if block:
        await message.answer("\n".join(block))

    # Подсказка администратору
    await message.answer("Чтобы подтвердить, отправь: /confirm <external_id>\nНапример: /confirm 123456")

from aiogram.filters import Command  # если уже есть — не дублируй

@dp.message(Command("confirm"))
async def cmd_confirm(message: types.Message):
    uid = message.from_user.id
    if not is_admin(uid):
        await message.answer("Недостаточно прав.")
        return

    parts = (message.text or "").strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи внешний ID: /confirm 123456")
        return

    ext_id = parts[1].strip()
    if not ext_id.isdigit():
        await message.answer("ID должен состоять только из цифр: /confirm 123456")
        return

    try:
        with open(USERS_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)

            # Ищем пользователя: ext_id совпадает, подтверждение ожидает, доступ ещё не выдан
            target = next(
                (u for u in data.get("users", [])
                 if u.get("external_id") == ext_id and u.get("confirm") and not u.get("reg")),
                None
            )

            if not target:
                await message.answer("ID не найден среди ожидающих подтверждения.")
                return

            # Обновляем статус
            target["reg"] = True          # доступ выдан
            target["confirm"] = False     # больше не ждёт проверки
            target["external_id"] = ""    # очищаем введённый ID

            # Сохраняем файл
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

        # Ответ админу
        uname = f"@{target.get('username')}" if target.get("username") else "(no username)"
        await message.answer(f"OK ✅ Подтверждён: {target.get('name','')} {uname} (tg_id={target.get('id')}).")

        # Уведомление пользователю
        try:
            # используем RU по умолчанию; если у тебя хранится lang — подставь его
            t = TRANSLATIONS.get("ru", TRANSLATIONS["en"])
            await bot.send_message(target["id"], t.get("reg_approved", "✅ Ваш ID подтверждён. Доступ открыт!"))
        except Exception:
            # молча игнорируем, если пользователь недоступен
            pass

    except Exception:
        logging.exception("/confirm failed")
        await message.answer("Ошибка при подтверждении. Проверь логи сервера.")



@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    register_user_if_new(message.from_user)
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text=f"🇷🇺 Русский", 
        callback_data=f"lang_ru"
    )

    await message.answer(
        TRANSLATIONS["en"]["welcome"],
        reply_markup=builder.as_markup()
    )

@dp.message(Command("dep"))
async def cmd_dep(message: types.Message):
    uid = message.from_user.id
    if not is_admin(uid):
        await message.answer("Недостаточно прав.")
        return

    parts = (message.text or "").strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи ID: /dep 123456  (может быть external_id или tg_id)")
        return

    arg = parts[1].strip()
    if not arg.isdigit():
        await message.answer("ID должен содержать только цифры.")
        return

    try:
        with open(USERS_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            users = data.get("users", [])

            # сначала ищем по external_id
            target = next((u for u in users if u.get("external_id") == arg), None)

            # если не нашли — ищем по tg_id
            if not target:
                arg_id = int(arg)
                target = next((u for u in users if u.get("id") == arg_id), None)

            if not target:
                await message.answer("Пользователь с таким ID не найден.")
                return

            target["dep"] = True

            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

        uname = f"@{target.get('username')}" if target.get("username") else "(no username)"
        await message.answer(f"✅ DEP установлен: {target.get('name','')} {uname} (tg_id={target.get('id')}).")

        # уведомляем пользователя
        try:
            await bot.send_message(target["id"], "✅ Ваш депозит подтверждён (dep=True).")
        except Exception:
            pass

    except Exception:
        logging.exception("/dep failed")
        await message.answer("Ошибка при установке dep. Проверь логи сервера.")


@dp.message(Command("decline"))
async def cmd_decline(message: types.Message):
    uid = message.from_user.id
    if not is_admin(uid):
        await message.answer("Недостаточно прав.")
        return

    parts = (message.text or "").strip().split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажи внешний ID: /decline 123456")
        return

    ext_id = parts[1].strip()
    if not ext_id.isdigit():
        await message.answer("ID должен состоять только из цифр: /decline 123456")
        return

    try:
        with open(USERS_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)

            target = next(
                (u for u in data.get("users", [])
                 if u.get("external_id") == ext_id and u.get("confirm") and not u.get("reg")),
                None
            )

            if not target:
                await message.answer("ID не найден среди заявок на подтверждение.")
                return

            # Отклоняем заявку
            target["confirm"] = False
            target["external_id"] = ""   # очищаем введённый ID
            # target["reg"] оставляем как есть (обычно False)

            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

        # Ответ админу
        uname = f"@{target.get('username')}" if target.get("username") else "(no username)"
        await message.answer(f"Отклонено ❌: {target.get('name','')} {uname} (tg_id={target.get('id')}).")

        # Уведомление пользователю
        try:
            t = TRANSLATIONS.get("ru", TRANSLATIONS["en"])
            await bot.send_message(
                target["id"],
                t.get("reg_declined", "❌ Ваш ID отклонён. Проверьте корректность и отправьте снова.")
            )
        except Exception:
            pass

    except Exception:
        logging.exception("/decline failed")
        await message.answer("Ошибка при отклонении. Проверь логи сервера.")

@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_data[callback.from_user.id] = {"lang": lang}
    
    await callback.message.delete()
    
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=translations["subscribe_btn"],
            url=CHANNEL_LINK
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=translations["check"],
            callback_data="check_subscription"
        )
    )
    
    await callback.message.answer(
        translations["subscribe"],
        reply_markup=builder.as_markup()
    )

@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "en")
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            await callback.message.delete()
            
            temp_msg = await callback.message.answer(translations["access_granted"])
            
            await temp_msg.delete()
            
            user_data[user_id]["last_message_id"] = await show_main_menu(user_id, lang)
        else:
            await callback.answer(translations["not_subscribed"], show_alert=True)
    except Exception as e:
        logging.error(f"Subscription error: {e}")
        await callback.answer(translations["check_error"], show_alert=True)


@dp.message(lambda message: message.text in [TRANSLATIONS[lang]["reg"] for lang in LANGUAGES])
async def process_registration_button(message: types.Message):
    user_id = message.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "en")
    last_message_id = user_data.get(user_id, {}).get("last_message_id")
    if last_message_id:
        try:
            await bot.delete_message(chat_id=user_id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Error deleting main menu message: {e}")
    await bot.delete_message(chat_id=user_id, message_id=message.message_id)
    user_data[user_id]["last_message_id"] = await show_registration(user_id, lang, user_id=user_id)
    user_data[user_id]["last_stage"] = "registration"

@dp.message(lambda message: message.text in [TRANSLATIONS[lang]["algo"] for lang in LANGUAGES])
async def process_algo_button(message: types.Message):
    user_id = message.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "en")
    last_message_id = user_data.get(user_id, {}).get("last_message_id")
    if last_message_id:
        try:
            await bot.delete_message(chat_id=user_id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Error deleting main menu message: {e}")
    await bot.delete_message(chat_id=user_id, message_id=message.message_id)
    user_data[user_id]["last_message_id"] = await show_main_menu(user_id, lang)

@dp.message(lambda message: message.text in [TRANSLATIONS[lang]["support"] for lang in LANGUAGES])
async def process_support(message: types.Message):
    user_id = message.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "en")
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text=translations.get("reg", "📝 Registration")),
        types.KeyboardButton(text=translations.get("instr", "📚 Instructions"))
    )
    builder.row(types.KeyboardButton(text=translations.get("support", "🛠 Support")))
    builder.row(types.KeyboardButton(text="🚀 Get a signal"))

    await message.answer(
        translations.get("support_text", "Свяжитесь с поддержкой: @maboy_poderzhka"),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(lambda message: message.text in [TRANSLATIONS[lang]["back"] for lang in LANGUAGES])
async def process_back(message: types.Message):
    user_id = message.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "en")
    
    # Удаляем сообщение с кнопкой "Назад"
      # Задержка 2 секунды
    await bot.delete_message(chat_id=user_id, message_id=message.message_id)
    
    # Удаляем предыдущее сообщение (регистрации)
    last_message_id = user_data.get(user_id, {}).get("last_message_id")
    if last_message_id:
        try:
              # Задержка 2 секунды
            await bot.delete_message(chat_id=user_id, message_id=last_message_id)
        except Exception as e:
            logging.error(f"Error deleting registration message: {e}")
    
    # Показываем главное меню
    user_data[user_id]["last_message_id"] = await show_main_menu(user_id, lang)

async def set_bot_description():
    await bot.set_my_description(BOT_DESCRIPTION)

async def main():
    await set_bot_description()
    await dp.start_polling(bot)

@dp.message(lambda message: message.text in [TRANSLATIONS[lang]["instr"] for lang in LANGUAGES])
async def process_instruction(message: types.Message):
    user_id = message.from_user.id
    lang = user_data.get(user_id, {}).get("lang", "en") 
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text=translations.get("reg", "📝 Registration")),
        types.KeyboardButton(text=translations.get("instr", "📚 Instructions"))
    )
    builder.row(types.KeyboardButton(text=translations.get("support", "🛠 Support")))
    builder.row(types.KeyboardButton(text="🚀 Get a signal"))

    await message.answer(
        translations.get("instructions", "Инструкция недоступна"),
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

def has_signal_access(user_id: int) -> bool:
    """
    Доступ к сигналам: admin==True ИЛИ reg==True.
    На всякий случай поддерживаем опечатку 'rec'.
    """
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        u = next((u for u in data.get("users", []) if u.get("id") == user_id), None)
        if not u:
            return False
        return bool(u.get("admin")) or (bool(u.get("reg")) and bool(u.get("dep")))
    except Exception:
        logging.exception("has_signal_access failed")
        return False

import random

@dp.message(lambda message: message.text == "🚀 Get a signal")
async def handle_signal_button(message: types.Message):
    if not has_signal_access(message.from_user.id):
        await message.answer("❌ Нет доступа к сигналам. Завершите регистрацию и внесите депозит или войдите как админ. Депозит подтверждается в течение 10 минут. ")
    else:
        global current_signal
        # если нет сигнала или он уже истёк — создаём новый
        if not current_signal["trend"] or time.time() > current_signal["expires"]:
            current_signal = generate_signal()

        trend = current_signal["trend"]
        minutes = int((current_signal["expires"] - time.time()) // 60)  # сколько осталось
        text = (
            "📢 Общий сигнал AUD/CAD\n"
            f"• Тренд: {trend}\n"
            f"• Оставшееся время: {minutes} min."
        )
        await message.answer(text)

@dp.message()
async def catch_external_id(message: types.Message):
    uid = message.from_user.id
    stage = user_data.get(uid, {}).get("last_stage")
    if stage != "awaiting_external_id":
        return  # не наша стадия — пропускаем

    lang = user_data.get(uid, {}).get("lang", "ru")
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    text = (message.text or "").strip()

    # принимаем только цифры, 3..20 символов
    if not re.fullmatch(r"\d{3,20}", text):
        await message.answer(
            t.get("ask_external_id", "Пришлите ваш ID одним сообщением (только цифры).")
        )
        return

    # сохраняем external_id и confirm=True
    try:
        with open(USERS_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)

            # запрещаем дубли ID у разных пользователей
            for u in data.get("users", []):
                if u.get("external_id") == text and u.get("id") != uid:
                    await message.answer("Этот ID уже используется. Проверьте и отправьте другой.")
                    return

            found = False
            for u in data.get("users", []):
                if u.get("id") == uid:
                    u["external_id"] = text
                    u["confirm"] = True
                    found = True
                    break

            if not found:
                data.setdefault("users", []).append({
                    "id": uid,
                    "name": message.from_user.full_name,
                    "username": message.from_user.username or "",
                    "reg": False,
                    "confirm": True,
                    "external_id": text,
                    "admin": False,
                    "amount": 0
                })

            f.seek(0); json.dump(data, f, ensure_ascii=False, indent=4); f.truncate()
    except Exception:
        logging.exception("saving external_id failed")
        await message.answer("Ошибка сохранения ID. Попробуйте ещё раз позже.")
        return

    # переводим в ожидание модерации и сообщаем пользователю
    user_data[uid]["last_stage"] = "waiting_admin_review"
    # Отправляем подсказку-картинку, где искать ID
    try:
        help_path = Path(__file__).parent / "assets" / "help.jpeg"
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=FSInputFile(help_path),
            caption="Где найти ваш ID — пример на скриншоте."
        )
    except Exception:
        logging.exception("Не удалось отправить help.jpeg")

    await message.answer(
        t.get("await_admin_review", "Спасибо! Ваш ID получен. Ожидайте подтверждения администратором.")
    )

    # уведомляем админов (если оставил функцию — она без изменений)
    await notify_admins_about_confirmation(uid)



if __name__ == "__main__":
    asyncio.run(main())  

