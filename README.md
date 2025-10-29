# MyVibe Telegram Bot

Каркас проекта на основе bot-development-guide.

## Быстрый старт

1. Создай виртуальное окружение и установи зависимости:
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```
2. Скопируй переменные и укажи BOT_TOKEN:
```
cp .env.example .env
```
3. Запусти бота:
```
python -m app.main
```

## Структура
Слои: app (вход, контейнер, конфиг), core (домен), services (бизнес-оркестрация), handlers (презентация), infrastructure (БД, кеш, внешние клиенты, логирование), middleware, utils, plugins, tests, requirements.
