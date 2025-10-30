from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.database.connection import session_scope
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.role_repository import RoleRepository

DIALOGS = {}


def register_user_manage_dialog(router: Router):
    @router.message(Command("access"))
    async def access_entry(message: Message):
        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Добавить пользователя", callback_data="access:add")
        kb.button(text="➖ Удалить пользователя", callback_data="access:remove")
        kb.button(text="❌ Отмена", callback_data="access:cancel")
        kb.adjust(1)
        await message.answer("Выберите действие:", reply_markup=kb.as_markup())

    @router.callback_query(F.data == "access:add")
    async def step_add_start(cb: CallbackQuery):
        DIALOGS[cb.from_user.id] = {"flow": "add", "step": 1}
        kb = InlineKeyboardBuilder().button(text="⬅️ Назад", callback_data="access:back_root").adjust(1)
        await cb.message.edit_text("Введите Telegram ID пользователя (число):", reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data == "access:remove")
    async def step_remove_start(cb: CallbackQuery):
        DIALOGS[cb.from_user.id] = {"flow": "remove", "step": 1}
        with session_scope() as s:
            users = UserRepository(s).list_active()
            items = [(u.telegram_user_id, (u.full_name or "?") + f" ({u.telegram_user_id})") for u in users]
        kb = InlineKeyboardBuilder()
        for uid, label in items:
            kb.button(text=label, callback_data=f"access:pick_user:{uid}")
        kb.button(text="⬅️ Назад", callback_data="access:back_root")
        kb.adjust(1)
        await cb.message.edit_text("Выберите пользователя для удаления:", reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data.startswith("access:pick_user:"))
    async def remove_pick_user(cb: CallbackQuery):
        uid = int(cb.data.split(":")[-1])
        DIALOGS[cb.from_user.id] = {"flow": "remove", "step": 2, "telegram_id": uid}
        # Берём только примитивы из ORM внутри сессии
        with session_scope() as s:
            u = UserRepository(s).get_by_tg_id(uid)
            full_name = u.full_name if u else None
            role_id = u.role_id if u else None
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Удалить", callback_data="access:confirm_remove")
        kb.button(text="⬅️ Назад", callback_data="access:remove")
        kb.adjust(1)
        text = (
            "Подтвердите удаление:\n"
            f"• Telegram ID: {uid}\n"
            f"• Имя: {full_name or '—'}\n"
            f"• Роль ID: {role_id or '—'}"
        )
        await cb.message.edit_text(text, reply_markup=kb.as_markup())
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

    @router.message()
    async def dialog_text_handler(message: Message):
        dlg = DIALOGS.get(message.from_user.id)
        if not dlg:
            return
        if dlg["flow"] == "add":
            if dlg["step"] == 1:
                if not message.text.isdigit():
                    await message.answer("ID должен быть числом. Попробуйте снова.")
                    return
                dlg["telegram_id"] = int(message.text)
                dlg["step"] = 2
                kb = InlineKeyboardBuilder().button(text="⬅️ Назад", callback_data="access:back_id").adjust(1)
                await message.answer("Введите полное имя пользователя:", reply_markup=kb.as_markup())
                return
            if dlg["step"] == 2:
                dlg["full_name"] = message.text.strip()
                dlg["step"] = 3
                with session_scope() as s:
                    roles = [(r.id, r.role_name) for r in RoleRepository(s).list()]
                kb = InlineKeyboardBuilder()
                for rid, rname in roles:
                    kb.button(text=rname, callback_data=f"access:role:{rid}")
                kb.button(text="⬅️ Назад", callback_data="access:back_name")
                kb.adjust(2)
                await message.answer("Выберите роль:", reply_markup=kb.as_markup())
                return

    @router.callback_query(F.data == "access:back_id")
    async def back_from_name(cb: CallbackQuery):
        dlg = DIALOGS.get(cb.from_user.id)
        if dlg:
            dlg["step"] = 1
        kb = InlineKeyboardBuilder().button(text="⬅️ Назад", callback_data="access:back_root").adjust(1)
        await cb.message.edit_text("Введите Telegram ID пользователя (число):", reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data == "access:back_name")
    async def back_from_role(cb: CallbackQuery):
        dlg = DIALOGS.get(cb.from_user.id)
        if dlg:
            dlg["step"] = 2
        kb = InlineKeyboardBuilder().button(text="⬅️ Назад", callback_data="access:back_id").adjust(1)
        await cb.message.edit_text("Введите полное имя пользователя:", reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data.startswith("access:role:"))
    async def choose_role(cb: CallbackQuery):
        dlg = DIALOGS.get(cb.from_user.id)
        if not dlg:
            await cb.answer(); return
        role_id = int(cb.data.split(":")[-1])
        dlg["role_id"] = role_id
        dlg["step"] = 4
        with session_scope() as s:
            role = RoleRepository(s).get_by_id(role_id)
            role_name = role.role_name if role else str(role_id)
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Подтвердить", callback_data="access:confirm_add")
        kb.button(text="✏️ Изменить", callback_data="access:back_root")
        kb.adjust(2)
        text = (
            "Подтверждение добавления:\n"
            f"• Telegram ID: {dlg['telegram_id']}\n"
            f"• Имя: {dlg['full_name']}\n"
            f"• Роль: {role_name}"
        )
        await cb.message.edit_text(text, reply_markup=kb.as_markup())
        await cb.answer()

    @router.callback_query(F.data == "access:confirm_add")
    async def confirm_add(cb: CallbackQuery):
        dlg = DIALOGS.pop(cb.from_user.id, None)
        if not dlg:
            await cb.answer(); return
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
            await cb.answer(); return
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
