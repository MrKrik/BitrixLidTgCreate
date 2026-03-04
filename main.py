import os
import logging
import requests
import asyncio
from datetime import datetime, timedelta, timezone
from enum import Enum

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, User
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BITRIX_WEBHOOK = os.getenv("BITRIX_WEBHOOK")

bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM States для сбора контактных данных
class ContactForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    confirmation = State()



# ============ BITRIX24 API FUNCTIONS ============

def create_lead_in_bitrix(name: str, phone: str, username: str) -> bool:
    """
    Создает лид в Bitrix24 с переданными контактными данными
    """
    method = 'crm.lead.add'
    url = f"{BITRIX_WEBHOOK}{method}"
    
    # Формируем название лида
    lead_title = f"Лид от {name}"
    
    # Подготавливаем данные для создания лида
    params = {
        'fields': {
            'TITLE': lead_title,
            'NAME': name,
            'PHONE': [{'VALUE': phone, 'VALUE_TYPE': 'WORK'}],
            'COMMENTS': f"Telegram username: @{username}"
        }
    }
    
    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
        data = response.json()
        
        if 'result' in data and data['result']:
            lead_id = data['result']
            logging.info(f"Лид успешно создан в Bitrix24. ID: {lead_id}, Имя: {name}, Телефон: {phone}, Username: @{username}")
            return True
        else:
            logging.error(f"Ошибка при создании лида. Ответ: {data}")
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к Bitrix24 API: {e}")
        return False


# ============ TELEGRAM BOT HANDLERS ============

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Команда /start - начало сбора контактных данных"""
    await message.answer(
        "👋 Привет! Я помогу создать заявку в нашей CRM системе.\n\n"
        "Пожалуйста, укажите ваше имя и номер телефона.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ContactForm.waiting_for_name)


@dp.message(ContactForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени пользователя"""
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("❌ Пожалуйста, введите корректное имя (минимум 2 символа).")
        return
    
    await state.update_data(name=message.text.strip())
    await state.set_state(ContactForm.waiting_for_phone)
    await message.answer("✅ Спасибо! Теперь укажите ваш номер телефона (например, +7 (XXX) XXX-XX-XX):")


@dp.message(ContactForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона"""
    phone = message.text.strip()
    
    # Простая валидация телефона (есть цифры)
    if not any(char.isdigit() for char in phone):
        await message.answer("❌ Пожалуйста, введите корректный номер телефона.")
        return
    
    user_data = await state.get_data()
    
    await state.update_data(phone=phone)
    await state.set_state(ContactForm.confirmation)
    
    # Получаем username пользователя
    username = message.from_user.username or "не указано"
    
    # Формируем сообщение с подтверждением
    confirmation_text = (
        f"📋 Пожалуйста, подтвердите ваши данные:\n\n"
        f"👤 Имя: {user_data['name']}\n"
        f"📱 Телефон: {phone}\n"
        f"🔱 Telegram: @{username}\n\n"
        f"Все верно?"
    )
    
    # Создаем клавиатуру подтверждения
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Верно")
    builder.button(text="❌ Изменить")
    builder.adjust(2)
    
    await message.answer(confirmation_text, reply_markup=builder.as_markup())
    await state.update_data(username=username)


@dp.message(ContactForm.confirmation, F.text == "✅ Верно")
async def confirm_data(message: Message, state: FSMContext):
    """Подтверждение и создание лида в Bitrix24"""
    user_data = await state.get_data()
    
    # Создаем лид в Bitrix24
    success = create_lead_in_bitrix(
        name=user_data['name'],
        phone=user_data['phone'],
        username=user_data['username']
    )
    
    if success:
        await message.answer(
            "✅ Спасибо! Ваша заявка успешно создана.\n\n"
            "Наша команда вскоре свяжется с вами по указанному номеру телефона.",
            reply_markup=ReplyKeyboardRemove()
        )
        logging.info(f"Лид успешно создан для пользователя: {user_data['name']}")
    else:
        await message.answer(
            "❌ Произошла ошибка при создании заявки. Пожалуйста, попробуйте позже.",
            reply_markup=ReplyKeyboardRemove()
        )
        logging.error(f"Ошибка создания лида для: {user_data['name']}")
    
    await state.clear()


@dp.message(ContactForm.confirmation, F.text == "❌ Изменить")
async def edit_data(message: Message, state: FSMContext):
    """Редактирование данных"""
    await message.answer(
        "Давайте начнем заново. Пожалуйста, укажите ваше имя:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ContactForm.waiting_for_name)
    await state.update_data(name=None, phone=None)


@dp.message(ContactForm.waiting_for_name)
@dp.message(ContactForm.waiting_for_phone)
@dp.message(ContactForm.confirmation)
async def handle_invalid_input(message: Message):
    """Обработка некорректного ввода"""
    await message.answer(
        "⚠️ Пожалуйста, используйте форму снизу или введите корректные данные."
    )


# ============ MAIN ============

async def main():
    """Запуск диспетчера бота"""
    logging.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
