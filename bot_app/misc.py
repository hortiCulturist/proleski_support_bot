from aiogram import Bot, Dispatcher, Router

from bot_app.config import BOT_TOKEN

router = Router()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()