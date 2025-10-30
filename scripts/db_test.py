#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_test.py — простой тест соединения с БД и чтения таблиц.
Запуск из корня проекта:
    python -m scripts.db_test
"""
from __future__ import annotations

import os
from dotenv import load_dotenv

from infrastructure.database.connection import engine
from infrastructure.database.models import Role, User, Command
from sqlalchemy.orm import Session


def main():
    load_dotenv()
    print("DATABASE_URL:", os.getenv("DATABASE_URL"))

    # Подключение и простой запрос
    with Session(bind=engine) as s:
        # Пробуем выборку по основным таблицам
        roles = s.query(Role).all()
        users = s.query(User).all()
        commands = s.query(Command).all()

        print(f"OK: connected. rows -> roles={len(roles)}, users={len(users)}, commands={len(commands)}")
        # Выведем первые записи для наглядности
        if roles:
            print("role[0]:", roles[0].role_name)
        if users:
            print("user[0]:", users[0].telegram_user_id)
        if commands:
            print("command[0]:", commands[0].command_name)


if __name__ == "__main__":
    main()
