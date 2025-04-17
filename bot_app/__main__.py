import asyncio
from aiogram import Dispatcher, Router
from bot_app.misc import bot, dp
from bot_app.handlers.main import router

from bot_app.utils.neural_search import NeuralSearch
from bot_app.utils.neural_faq_handler import neural_router, initialize_neural_search


async def main():
    try:
        # Регистрируем роутеры
        dp.include_router(router)
        dp.include_router(neural_router)

        # Инициализируем нейросетевой поиск
        print("Начинаю инициализацию нейросетевого поиска...")
        await initialize_neural_search()
        print("Нейросетевой поиск успешно инициализирован")

        # Запускаем бота
        print("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске: {e}")


if __name__ == "__main__":
    asyncio.run(main())

# dp.include_router(router)
#
#
# async def main():
#     await dp.start_polling(bot)
#     dp.include_router(neural_router)
#     await initialize_neural_search()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())