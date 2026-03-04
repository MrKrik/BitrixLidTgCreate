# Telegram Bot с интеграцией Bitrix24 CRM

Чат-бот на aiogram3, который собирает контактные данные пользователя (имя и телефон) и автоматически создает лиды в системе CRM Bitrix24.

## 📋 Функциональность

- **Сбор контактных данных**: бот просит имя и номер телефона
- **Валидация**: проверка корректности введенных данных
- **Создание лидов**: автоматическое создание лида в Bitrix24 с полученными данными
- **Сохранение username**: включение Telegram username пользователя в комментарии лида
- **Подтверждение данных**: пользователь может проверить and исправить введенные данные перед отправкой

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте файл `.env` и добавьте ваши данные:

```
TELEGRAM_TOKEN=ваш_токен_бота_от_BotFather
BITRIX_WEBHOOK=https://your_domain.bitrix24.com/rest/webhook_id/
```

### 3. Получение токена Telegram

1. Напишите боту [@BotFather](https://t.me/botfather) в Telegram
2. Введите команду `/newbot`
3. Следуйте инструкциям и скопируйте полученный токен

### 4. Получение Webhook URL для Bitrix24

1. Перейдите в admin.bitrix24.ru
2. Установки → Приложения → CRM
3. Включите REST API
4. Создайте новый Webhook REST API
5. Скопируйте URL типа: `https://your_domain.bitrix24.com/rest/1/webhook_id/`

### 5. Запуск бота

```bash
python main.py
```

## 📱 Взаимодействие с ботом

1. **Пользователь запускает** `/start`
2. **Бот просит имя** - пользователь вводит свое имя
3. **Бот просит телефон** - пользователь вводит номер телефона
4. **Подтверждение** - бот показывает все данные (имя, телефон, username) и просит подтверждение
5. **Создание лида** - при подтверждении лид создается в Bitrix24

## 🔧 Структура кода

### Состояния FSM (Finite State Machine)
- `waiting_for_name` - ожидание ввода имени
- `waiting_for_phone` - ожидание ввода номера телефона
- `confirmation` - ожидание подтверждения данных

### Основные функции

**`create_lead_in_bitrix()`** - Создает лид в Bitrix24 с параметрами:
- `name` - имя клиента
- `phone` - номер телефона
- `username` - Telegram username

## 📊 Данные, отправляемые в Bitrix24

При создании лида отправляются:
- **TITLE** - название лида (например: "Лид от Иван Петров")
- **NAME** - имя контакта
- **PHONE** - массив с номером телефона и типом (WORK)
- **COMMENTS** - Telegram username в format: "Telegram username: @username"

## ⚙️ Возможные настройки

Вы можете расширить функциональность, добавив:

### Дополнительные поля при создании лида

Отредактируйте функцию `create_lead_in_bitrix()`:

```python
params = {
    'fields': {
        'TITLE': lead_title,
        'NAME': name,
        'PHONE': [{'VALUE': phone, 'VALUE_TYPE': 'WORK'}],
        'EMAIL': [{'VALUE': email, 'VALUE_TYPE': 'WORK'}],  # Добавить email
        'COMMENTS': f"Telegram username: @{username}",
        'SOURCE_ID': 'WEB'  # Источник лида
    }
}
```

### Дополнительные поля в форме

Добавьте новые State в `ContactForm` и обработчики:

```python
class ContactForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()  # Новое поле
    confirmation = State()
```

## 🛠️ Troubleshooting

### Ошибка: "TELEGRAM_TOKEN не найден"
- Убедитесь, что создан файл `.env`
- Проверьте, что в `.env` указан `TELEGRAM_TOKEN`

### Ошибка: "Ошибка при запросе к Bitrix24 API"
- Проверьте URL Webhook'а (должен быть вида: `https://...bitrix24.com/rest/webhook_id/`)
- Убедитесь, что Webhook активен в Bitrix24
- Проверьте, что в URL нет опечаток

### Лид не создается
- Проверьте логи - причина будет написана в консоли
- Убедитесь, что достаточно прав в Bitrix24 для создания лидов
- Проверьте, что поля в Bitrix24 корректно настроены

## 📝 Лицензия

MIT

## 👨‍💻 Автор

Развернуто на aiogram3 для интеграции с Bitrix24 CRM.
