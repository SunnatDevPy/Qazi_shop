from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def language_inl():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text='🇺🇿Uz', callback_data='lang_uz'),
              InlineKeyboardButton(text='🇷🇺Ru', callback_data='lang_rus')])
    ikb.adjust(2)
    return ikb.as_markup()


def confirm_register_inl():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text='✅Tasdiqlash✅', callback_data=f'confirm_register'),
              InlineKeyboardButton(text='❌Cancel❌', callback_data=f'cancel_register')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


async def my_address(address, user_id):
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text=i.address, callback_data=f'address_{user_id}_{i.lat}_{i.long}_{i.id}') for i in
              address])
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()


async def my_restorator(address, user_id):
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text=i.address, callback_data=f'address_{user_id}_{i.lat}_{i.long}_{i.id}') for i in
              address])
    ikb.adjust(1, repeat=True)
    return ikb.as_markup()


def main_menu():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="🍽Menu🍽", callback_data="menu"),
              InlineKeyboardButton(text="Admin Panel", callback_data="admin")])
    return ikb.as_markup()


def menu(user_id, admin=False):
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text="🛒QAZI BOT🛒",
                                   web_app=WebAppInfo(
                                       url=f'https://www.youtube.com/'))])
    if admin:
        ikb.add(*[InlineKeyboardButton(text="⚙️Settings⚙️", callback_data='game_settings')])
    ikb.adjust(1, 2)
    return ikb.as_markup()


def contact():
    ikb = ReplyKeyboardBuilder()
    ikb.row(KeyboardButton(text='📞 Contact 📞', request_contact=True))
    return ikb.as_markup(resize_keyboard=True)


def confirm_inl():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[InlineKeyboardButton(text='✅Tasdiqlash✅', callback_data=f'confirm_network'),
              InlineKeyboardButton(text="❌Toxtatish❌", callback_data=f'cancel_network')])
    ikb.adjust(2, repeat=True)
    return ikb.as_markup()


def get_location():
    kb = ReplyKeyboardBuilder()
    kb.add(*[KeyboardButton(text='📍Locatsiya jonatish📍', request_location=True)])
    return kb.as_markup(resize_keyboard=True)
