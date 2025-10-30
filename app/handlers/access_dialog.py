from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.database.connection import session_scope
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.role_repository import RoleRepository

# Состояния диалога в памяти (простая FSM без хранилища)
DIALOGS = {}


def register_user_manage_dialog(router: Router):
    """Регистрация диалога добавления/удаления пользователя.
    Поток: /access -> кнопки [Добавить][Удалить] -> шаги с возвратом назад.
    """

    @router.message(Command("access"))
    async def access_entry(message: Message):
        # Только если пользователь есть в БД и является админом — проверка должна быть снаружи, здесь опускаем
        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Добавить пользователя", callback_data="access:add")
        kb.button(text="➖ Удалить пользователя", callback_data="access:remove")
        kb.button(text="❌ Отмена", callback_data="access:cancel")
        kb.adjust(1)
        await message.answer("Выберите действие:", reply_markup=kb.as_markup())

    # Шаг 1: выбор действия -> запрос Telegram ID
    @router.callback_query(F.data == "access:add")
    async def step_add_start(cb: CallbackQuery):
        DIALOGS[cb.from_user.id] = {"flow": "add", "step": 1}
        kb = InlineKeyboardBuilder()
        kb.button(text="⬅️ Назад", callback_data="access:back_root")
        await cb.message.edit_text("Введите Telegram ID пользователя (число):", reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data == "access:remove")
    async def step_remove_start(cb: CallbackQuery):
        DIALOGS[cb.from_user.id] = {"flow": "remove", "step": 1}
        kb = InlineKeyboardBuilder()
        kb.button(text="⬅️ Назад", callback_data="access:back_root")
        await cb.message.edit_text("Введите Telegram ID пользователя для удаления:", reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data == "access:back_root")
    async def back_to_root(cb: CallbackQuery):
        DIALOGS.pop(cb.from_user.id, None)
        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Добавить пользователя", callback_data="access:add")
        kb.button(text="➖ Удалить пользователя", callback_data="access:remove")
        kb.button(text="❌ Отмена", callback_data="access:cancel")
        kb.adjust(1)
        await cb.message.edit_text("Выберите действие:", reply_markup=kb.as_markup())
        await cb.answer()

    # Обработка текстовых ответов по шагам
    @router.message()
    async def dialog_text_handler(message: Message):
        dlg = DIALOGS.get(message.from_user.id)
        if not dlg:
            return  # не в диалоге

        if dlg["flow"] == "add":
            if dlg["step"] == 1:
                # получили Telegram ID
                if not message.text.isdigit():
                    await message.answer("ID должен быть числом. Попробуйте снова.")
                    return
                dlg["telegram_id"] = int(message.text)
                dlg["step"] = 2
                # попросим имя
                kb = InlineKeyboardBuilder()
                kb.button(text="⬅️ Назад", callback_data="access:back_id")
                await message.answer("Введите полное имя пользователя:", reply_markup=kb.as_markup())
                return
        
            if dlg["step"] == 2:
                dlg["full_name"] = message.text.strip()
                dlg["step"] = 3
                # выбор роли кнопками
                with session_scope() as s:
                    roles = RoleRepository(s).get_all()
                kb = InlineKeyboardBuilder()
                for r in roles:
                    kb.button(text=r.rolename, callback_data=f"access:role:{r.id}")
                kb.button(text="⬅️ Назад", callback_data="access:back_name")
                kb.adjust(2)
                await message.answer("Выберите роль:", reply_markup=kb.as_markup())
                return

        elif dlg["flow"] == "remove":
            if dlg["step"] == 1:
                if not message.text.isdigit():
                    await message.answer("ID должен быть числом. Попробуйте снова.")
                    return
                dlg["telegram_id"] = int(message.text)
                # подтверждение удаления
                with session_scope() as s:
                    repo = UserRepository(s)
                    user = repo.get_by_tg_id(dlg["telegram_id"])
                kb = InlineKeyboardBuilder()
                kb.button(text="✅ Подтвердить удаление", callback_data="access:confirm_remove")
                kb.button(text="⬅️ Назад", callback_data="access:back_root")
                text = (
                    "Подтвердите удаление:\n"
                    f"• Telegram ID: {dlg['telegram_id']}\n"
                    f"• В БД: {'найден' if user else 'не найден'}"
                )
                await message.answer(text, reply_markup=kb.as_markup())
                dlg["step"] = 2
                return

    # Навигация назад в add-flow
    @router.callback_query(F.data == "access:back_id")
    async def back_from_name(cb: CallbackQuery):
        dlg = DIALOGS.get(cb.from_user.id)
        if dlg:
            dlg["step"] = 1
        kb = InlineKeyboardBuilder()
        kb.button(text="⬅️ Назад", callback_data="access:back_root")
        await cb.message.edit_text("Введите Telegram ID пользователя (число):", reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data == "access:back_name")
    async def back_from_role(cb: CallbackQuery):
        dlg = DIALOGS.get(cb.from_user.id)
        if dlg:
            dlg["step"] = 2
        kb = InlineKeyboardBuilder()
        kb.button(text="⬅️ Назад", callback_data="access:back_id")
        await cb.message.edit_text("Введите полное имя пользователя:", reply_markup=kb.as_markup())
        await cb.answer()

    # Выбор роли
    @router.callback_query(F.data.startswith("access:role:"))
    async def choose_role(cb: CallbackQuery):
        dlg = DIALOGS.get(cb.from_user.id)
        if not dlg:
            await cb.answer()
            return
        role_id = int(cb.data.split(":")[-1])
        dlg["role_id"] = role_id
        dlg["step"] = 4
        # Подтверждение
        with session_scope() as s:
            role = RoleRepository(s).get_by_id(role_id)
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Подтвердить", callback_data="access:confirm_add")
        kb.button(text="✏️ Изменить", callback_data="access:back_root")
        kb.adjust(2)
        text = (
            "Подтверждение добавления:\n"
            f"• Telegram ID: {dlg['telegram_id']}\n"
            f"• Имя: {dlg['full_name']}\n"
            f"• Роль: {role.rolename if role else role_id}"
        )
        await cb.message.edit_text(text, reply_markup=kb.as_markup())
        await cb.answer()

    # Подтверждения
    @router.callback_query(F.data == "access:confirm_add")
    async def confirm_add(cb: CallbackQuery):
        dlg = DIALOGS.pop(cb.from_user.id, None)
        if not dlg:
            await cb.answer()
            return
        with session_scope() as s:
            users = UserRepository(s)
            user = users.get_by_tg_id(dlg["telegram_id"])
            if user is None:
                users.create(dlg["telegram_id"], None, dlg.get("full_name"), dlg["role_id"]) 
                text = "✅ Пользователь успешно добавлен"
            else:
                users.set_role(user.id, dlg["role_id"])
                text = "✅ Роль пользователя обновлена"
        await cb.message.edit_text(text)
        await cb.answer()

    @router.callback_query(F.data == "access:confirm_remove")
    async def confirm_remove(cb: CallbackQuery):
        dlg = DIALOGS.pop(cb.from_user.id, None)
        if not dlg:
            await cb.answer()
            return
        with session_scope() as s:
            users = UserRepository(s)
            user = users.get_by_tg_id(dlg["telegram_id"])
            if user is None:
                text = "ℹ️ Пользователь не найден"
            else:
                users.deactivate(user.id)
                text = "✅ Пользователь деактивирован"
        await cb.message.edit_text(text)
        await cb.answer()

    @router.callback_query(F.data == "access:cancel")
    async def cancel_dialog(cb: CallbackQuery):
        DIALOGS.pop(cb.from_user.id, None)
        await cb.message.edit_text("Отменено")
        await cb.answer()
