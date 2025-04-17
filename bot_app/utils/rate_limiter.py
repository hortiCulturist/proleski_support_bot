from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Словарь для хранения информации о запросах пользователей
# Ключ - user_id, значение - список временных меток запросов
user_requests: Dict[int, List[datetime]] = defaultdict(list)

# Максимальное количество запросов в течение периода
MAX_REQUESTS = 5

# Период ограничения в секундах (60 секунд = 1 минута)
RATE_LIMIT_PERIOD = 60


async def check_rate_limit(user_id: int) -> Tuple[bool, Optional[int]]:
    """
    Проверяет превышен ли лимит запросов для пользователя.
    """

    current_time = datetime.now()

    user_requests[user_id] = [
        req_time for req_time in user_requests[user_id]
        if current_time - req_time < timedelta(seconds=RATE_LIMIT_PERIOD)
    ]

    # Проверяем, не превышен ли лимит
    if len(user_requests[user_id]) >= MAX_REQUESTS:
        if user_requests[user_id]:
            oldest_request = min(user_requests[user_id])
            wait_seconds = RATE_LIMIT_PERIOD - (current_time - oldest_request).total_seconds()
            wait_seconds = max(0, int(wait_seconds))
            return False, wait_seconds
        return False, RATE_LIMIT_PERIOD

    # Добавляем текущий запрос в историю
    user_requests[user_id].append(current_time)
    return True, None


def get_rate_limit_message(wait_seconds: int, lang: str) -> str:
    """
    Возвращает сообщение о превышении лимита запросов на нужном языке.
    """
    if lang == "en":
        return f"⚠️ **Rate limit exceeded**. Please wait {wait_seconds} seconds before sending your next question."
    else:
        return f"⚠️ **Превышен лимит запросов**. Пожалуйста, подождите {wait_seconds} секунд перед отправкой следующего вопроса."