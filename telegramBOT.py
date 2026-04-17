import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from AI import askAItoAnswer
from database import saveUserData
from automation import filling
from URLS import urls

# Bot token for Telegram API interaction
TOKEN = '8355183430:AAFg6fmc8jxmG0jj797WcyTbFtfLskolrnY'

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handles the /start command. Welcomes user and checks DB for existing data."""
    response = await askAItoAnswer(str(message.from_user.id),
                                   "Привіт, використай данні з таблиці якщо є та привітайся зі мною.")
    await message.answer(response['reply'])


@dp.message()
async def handle_docs(message: types.Message):
    """Handles all text messages, processes them via AI, and saves data to DB."""
    response = await askAItoAnswer(str(message.from_user.id), message.text)
    await message.answer(response['reply'])

    apiData = response.get('data', {})

    # Save data only if all required fields are present to avoid partial records
    if apiData.get('name') and apiData.get('phone') and apiData.get('city'):
        saveUserData(message.from_user.id, apiData.get('name'), apiData.get('phone'), apiData.get('city'))

    # If AI gathered all info, show confirmation keyboard
    if response['is_complete']:
        confirmKb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='✅ Confirm', callback_data='confirmBooking'),
                InlineKeyboardButton(text='✏️ Edit', callback_data='changeData'),
                InlineKeyboardButton(text='❌ Cancel', callback_data='cancelBooking'),
            ]
        ])

        textMessage = (
            f"✅ *Please verify your booking details:* \n\n"
            f"👤 Name: {apiData.get('name')}\n"
            f"📞 Phone: {apiData.get('phone')}\n"
            f"🏙️ City: {apiData.get('city')}\n"
            f"📅 Date: {apiData.get('date')}"
        )

        await message.answer(textMessage, reply_markup=confirmKb, parse_mode='Markdown')


@dp.callback_query(F.data == 'confirmBooking')
async def confirmBooking(callback: CallbackQuery):
    """Processes the final booking step by launching browser automation."""
    await callback.message.answer('⏳ Processing your booking, please wait a few moments...')

    # Extract data from the last message context via AI
    response = await askAItoAnswer(str(callback.from_user.id), "Дістань данні з повідомлення")
    apiData = response.get('data', {})

    # Safely handle city name for URL mapping
    city = (apiData.get('city') or "").lower()
    url = urls.get(city)

    if not url:
        await callback.message.answer("❌ Error: Selected city is not supported for online booking.")
        return

    # Run synchronous Playwright function in a separate thread to keep bot responsive
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        filling,
        str(url), apiData.get('name'), apiData.get('phone'), apiData.get('date')
    )
    await callback.message.answer(f'✅ Successfully booked for {apiData.get("name")} in {city.capitalize()}!')


@dp.callback_query(F.data == 'changeData')
async def changeData(callback: CallbackQuery):
    """Handles the edit request."""
    response = await askAItoAnswer(str(callback.from_user.id), "Мені потрібно щось змінити з цих даних")
    await callback.message.answer(response['reply'])


@dp.callback_query(F.data == 'cancelBooking')
async def cancelBooking(callback: CallbackQuery):
    """Handles the cancellation request."""
    response = await askAItoAnswer(str(callback.from_user.id), "Я передумав відміни бронювання")
    await callback.message.answer(response['reply'])


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())