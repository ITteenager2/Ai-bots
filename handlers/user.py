from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import reply, inline
from services.content_generation import ContentGeneration
from database import db
from config import config
import logging

router = Router()

class UserStates(StatesGroup):
    main_menu = State()
    chatgpt = State()
    gpt4o = State()
    imagine = State()
    premium_purchase = State()
    course = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if not await check_subscription(message.bot, user_id):
        builder = inline.get_subscription_keyboard()
        await message.answer(
            "🔒 Для использования бота необходимо подписаться на канал!\n"
            "После подписки нажмите 'Проверить подписку'",
            reply_markup=builder
        )
        return
    
    user = db.get_user(user_id)
    await message.answer(
        "🤖 Добро пожаловать в YarseoneiroAI!\n\n"
        "Доступные команды:\n"
        "/chatgpt - Диалог с GPT-4o mini (бесплатно)\n"
        "/gpt4o - Диалог с GPT-4o (платно)\n"
        "/imagine или /image - Создать изображение с DALL-E (платно)\n"
        "/profile - Ваш профиль и оставшиеся генерации\n"
        "/bonus - Пройти бесплатный курс для получения генераций\n"
        "/invite - Пригласить друзей и получить бонусы\n"
        "/premium - Купить Premium\n\n"
        f"У вас доступно: {user['free_generations']} бесплатных генераций\n\n"
        "Выберите действие из меню ниже 👇",
        reply_markup=reply.get_main_menu()
    )
    await state.set_state(UserStates.main_menu)

@router.message(F.text == "🤖 Генерация текста")
async def text_generation(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    model = "gpt-4o" if user['premium'] else "gpt-4o-mini"
    await message.answer(f"Введите ваш запрос для {model}:")
    await state.set_state(UserStates.chatgpt)

@router.message(F.text == "🎨 Генерация изображений")
async def image_generation(message: Message, state: FSMContext):
    await cmd_imagine(message, state)

@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    await cmd_profile(message)

@router.message(F.text == "⭐️ Premium")
async def premium(message: Message, state: FSMContext):
    await cmd_premium(message, state)

@router.message(F.text == "📚 Бонусный курс")
async def bonus_course(message: Message, state: FSMContext):
    await cmd_bonus(message, state)

@router.message(F.text == "👥 Пригласить друзей")
async def invite_friends(message: Message):
    await cmd_invite(message)

@router.message(Command("chatgpt"))
async def cmd_chatgpt(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    model = "gpt-4o" if user['premium'] else "gpt-4o-mini"
    await message.answer(f"Введите ваш запрос для {model}:")
    await state.set_state(UserStates.chatgpt)

@router.message(UserStates.chatgpt)
async def process_chatgpt(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    model = "gpt-4o" if user['premium'] else "gpt-4o-mini"
    response = await ContentGeneration.generate_text(message.text, model=model)
    await message.answer(response)
    await state.set_state(UserStates.main_menu)

@router.message(Command("gpt4o"))
async def cmd_gpt4o(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user['free_generations'] <= 0 and not user['premium']:
        await message.answer("У вас недостаточно генераций. Купите Premium или заработайте бонусы.")
        return
    model = "GPT-4o" if user['premium'] else "GPT-4o mini"
    await message.answer(f"Введите ваш запрос для {model}:")
    await state.set_state(UserStates.gpt4o)

@router.message(UserStates.gpt4o)
async def process_gpt4o(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if not user['premium']:
        if user['free_generations'] <= 0:
            await message.answer("У вас недостаточно генераций. Купите Premium или заработайте бонусы.")
            await state.set_state(UserStates.main_menu)
            return
        user['free_generations'] -= 1
        db.update_user(message.from_user.id, user)
    
    model = "gpt-4o" if user['premium'] else "gpt-4o-mini"
    response = await ContentGeneration.generate_text(message.text, model=model)
    await message.answer(response)
    await state.set_state(UserStates.main_menu)

@router.message(Command("imagine"))
@router.message(Command("image"))
async def cmd_imagine(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user['free_generations'] <= 0 and not user['premium']:
        await message.answer("У вас недостаточно генераций. Купите Premium или заработайте бонусы.")
        return
    await message.answer("Опишите изображение, которое хотите создать:")
    await state.set_state(UserStates.imagine)

@router.message(UserStates.imagine)
async def process_imagine(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if not user['premium']:
        user['free_generations'] -= 1
        db.update_user(message.from_user.id, user)
    image = await ContentGeneration.generate_image(message.text)
    if image:
        await message.answer_photo(photo=image)
    else:
        await message.answer("Не удалось сгенерировать изображение. Попробуйте еще раз.")
    await state.set_state(UserStates.main_menu)

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = db.get_user(message.from_user.id)
    profile_text = (
        f"👤 Ваш профиль:\n"
        f"🔢 Оставшиеся бесплатные генерации: {user['free_generations']}\n"
        f"🌟 Premium: {'Да' if user['premium'] else 'Нет'}\n"
        f"👥 Приглашено пользователей: {len(user['invited_users'])}\n"
        f"📚 Пройдено уроков: {len(user['completed_lessons'])}"
    )
    await message.answer(profile_text)

@router.message(Command("bonus"))
async def cmd_bonus(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if len(user['completed_lessons']) >= config.MAX_COURSE_BONUS // config.COURSE_BONUS:
        await message.answer("Вы уже прошли все уроки и получили максимальное количество бонусов.")
        return
    
    courses = db.get_all_lessons()
    next_lesson = len(courses) + 1
    
    if str(next_lesson) in courses:
        lesson = courses[str(next_lesson)]
        await message.answer(f"Урок {next_lesson}: {lesson['title']}\n\n{lesson['content']}")
        await message.answer("Нажмите 'Готово', когда закончите урок.", reply_markup=inline.get_lesson_complete_keyboard())
        await state.set_state(UserStates.course)
    else:
        await message.answer("Извините, новые уроки пока не доступны.")

@router.callback_query(F.data == "lesson_complete")
async def process_lesson_complete(callback: CallbackQuery, state: FSMContext):
    user = db.get_user(callback.from_user.id)
    next_lesson = len(user['completed_lessons']) + 1
    user['completed_lessons'].append(next_lesson)
    user['free_generations'] += config.COURSE_BONUS
    db.update_user(callback.from_user.id, user)
    await callback.message.answer(f"Урок пройден! Вы получили {config.COURSE_BONUS} бесплатных генераций.")
    await state.set_state(UserStates.main_menu)

@router.message(Command("invite"))
async def cmd_invite(message: Message):
    user_id = message.from_user.id
    bot_info = await message.bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start={user_id}"
    await message.answer(
        f"👥 Пригласите друга и получите {config.INVITE_BONUS} генераций!\n\n"
        f"Ваша реферальная ссылка: {invite_link}\n\n"
        "Когда ваш друг активирует бота по этой ссылке, вы получите бонус."
    )

@router.message(Command("premium"))
async def cmd_premium(message: Message, state: FSMContext):
    await message.answer(
        "🌟 Premium подписка\n\n"
        "Преимущества:\n"
        "- Неограниченное количество генераций\n"
        "- Доступ к эксклюзивным функциям\n"
        "- Приоритетная поддержка\n\n"
        "Стоимость: $9.99/месяц\n\n"
        "Для оформления подписки нажмите кнопку ниже:",
        reply_markup=inline.get_premium_keyboard()
    )
    await state.set_state(UserStates.premium_purchase)

@router.callback_query(F.data == "buy_premium")
async def process_buy_premium(callback: CallbackQuery, state: FSMContext):
    # Here you would implement the actual payment processing
    # For now, we'll just simulate activating Premium
    user = db.get_user(callback.from_user.id)
    user['premium'] = True
    user['free_generations'] += config.PREMIUM_GENERATIONS
    db.update_user(callback.from_user.id, user)
    await callback.message.answer(
        f"🎉 Поздравляем! Вы активировали Premium!\n"
        f"Вам начислено {config.PREMIUM_GENERATIONS} генераций."
    )
    await state.set_state(UserStates.main_menu)

async def check_subscription(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

