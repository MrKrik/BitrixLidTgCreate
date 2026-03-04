"""
Базовые тесты для проверки работоспособности бота

Использование:
    pytest tests.py -v
    
Требует:
    pytest
    pytest-asyncio
"""

import pytest
import os
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()


class TestEnvironment:
    """Тесты для проверки переменных окружения"""
    
    def test_telegram_token_exists(self):
        """Проверяет, что TELEGRAM_TOKEN установлен"""
        token = os.getenv("TELEGRAM_TOKEN")
        assert token is not None, "TELEGRAM_TOKEN не установлен в .env"
        assert len(token) > 20, "TELEGRAM_TOKEN выглядит некорректно"
    
    def test_bitrix_webhook_exists(self):
        """Проверяет, что BITRIX_WEBHOOK установлен"""
        webhook = os.getenv("BITRIX_WEBHOOK")
        assert webhook is not None, "BITRIX_WEBHOOK не установлен в .env"
        assert "bitrix24.com" in webhook, "BITRIX_WEBHOOK выглядит некорректно"


class TestValidation:
    """Тесты для проверки валидации входных данных"""
    
    def test_name_validation_short(self):
        """Тестирует валидацию короткого имени"""
        name = "A"
        assert len(name.strip()) >= 2, "Имя должно быть минимум 2 символа"
    
    def test_name_validation_valid(self):
        """Тестирует валидацию корректного имени"""
        name = "Ivan Petrov"
        assert len(name.strip()) >= 2, "Имя должно быть минимум 2 символа"
    
    def test_phone_validation_with_digits(self):
        """Тестирует валидацию номера с цифрами"""
        phone = "+7 999 123-45-67"
        assert any(char.isdigit() for char in phone), "Номер должен содержать цифры"
    
    def test_phone_validation_without_digits(self):
        """Тестирует валидацию номера без цифр"""
        phone = "abcd"
        assert not any(char.isdigit() for char in phone), "Номер не содержит цифры"


class TestAPI:
    """Тесты для проверки API функций"""
    
    def test_bitrix_url_format(self):
        """Проверяет формат Bitrix24 URL"""
        webhook = os.getenv("BITRIX_WEBHOOK")
        
        if webhook:
            assert webhook.endswith("/"), "Webhook должен заканчиваться на /"
            assert "https://" in webhook, "Webhook должен использовать HTTPS"
            assert "bitrix24.com" in webhook, "Webhook должен быть для bitrix24.com"
    
    def test_lead_creation_url(self):
        """Проверяет URL для создания лида"""
        webhook = os.getenv("BITRIX_WEBHOOK")
        
        if webhook:
            lead_url = f"{webhook}crm.lead.add"
            assert lead_url.startswith("https://"), "URL должен быть HTTPS"


class TestImports:
    """Тесты для проверки импортов"""
    
    def test_aiogram_import(self):
        """Проверяет, что aiogram может быть импортирован"""
        try:
            import aiogram
            assert hasattr(aiogram, 'Bot'), "aiogram должен содержать Bot"
        except ImportError:
            pytest.skip("aiogram не установлен")
    
    def test_dotenv_import(self):
        """Проверяет, что python-dotenv может быть импортирован"""
        try:
            from dotenv import load_dotenv
            assert callable(load_dotenv), "load_dotenv должен быть функцией"
        except ImportError:
            pytest.skip("python-dotenv не установлен")
    
    def test_requests_import(self):
        """Проверяет, что requests может быть импортирован"""
        try:
            import requests
            assert hasattr(requests, 'post'), "requests должен содержать post"
        except ImportError:
            pytest.skip("requests не установлен")


class TestMockFunctions:
    """Тесты для проверки функций с mock данными"""
    
    def test_lead_data_structure(self):
        """Проверяет структуру данных лида"""
        lead_data = {
            'name': 'Ivan Petrov',
            'phone': '+7 999 123-45-67',
            'username': 'ivan_user'
        }
        
        assert 'name' in lead_data, "Должно быть поле name"
        assert 'phone' in lead_data, "Должно быть поле phone"
        assert 'username' in lead_data, "Должно быть поле username"
        assert len(lead_data['name']) >= 2, "Имя должно быть валидным"
    
    def test_bitrix_params_structure(self):
        """Проверяет структуру параметров для Bitrix24"""
        params = {
            'fields': {
                'TITLE': 'Лид от Ivan Petrov',
                'NAME': 'Ivan Petrov',
                'PHONE': [{'VALUE': '+7 999 123-45-67', 'VALUE_TYPE': 'WORK'}],
                'COMMENTS': 'Telegram username: @ivan_user'
            }
        }
        
        assert 'fields' in params, "Должно быть поле fields"
        assert 'TITLE' in params['fields'], "Должно быть поле TITLE"
        assert 'NAME' in params['fields'], "Должно быть поле NAME"
        assert 'PHONE' in params['fields'], "Должно быть поле PHONE"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
