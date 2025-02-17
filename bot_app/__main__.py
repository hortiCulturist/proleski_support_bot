import asyncio
from aiogram import Dispatcher, Router
from bot_app.misc import bot, dp
from bot_app.handlers.main import router

dp.include_router(router)



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())