from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/yarseoneiro")],
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_image_size_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="1024x1024", callback_data="size_1024x1024")],
        [InlineKeyboardButton(text="512x512", callback_data="size_512x512")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_lesson_complete_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Готово", callback_data="lesson_complete")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_premium_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Купить Premium", callback_data="buy_premium")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

