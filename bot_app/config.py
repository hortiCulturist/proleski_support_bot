import os
import re

from dotenv import load_dotenv
from pymystem3 import Mystem

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
FILES_PATH = os.path.join(os.getcwd(), 'files')

sections_mapping = {
    "Описание тренажёров": "simulator_description",
    "Описание дополнительных опций": "option_description",
    "FAQ": "FAQ",
    "Другие вопросы": "other_issues"
}


FAQ_TEMPLATES = {
    'ru': {
        'choose_question': '🔍 Возможно, вы имели в виду один из этих вопросов:',
        'click_button': '\n👇Выберите номер подходящего вопроса'
    },
    'en': {
        'choose_question': '🔍 You may have had one of these questions in mind:',
        'click_button': '\n👇 Choose the number of the appropriate question'
    }
}

# Инициализируем анализатор Mystem
mystem = Mystem()

# Регулярное выражение для удаления знаков препинания
PUNCTUATION_PATTERN = re.compile(r'[^\w\s]')


# Нормализация слова с помощью Mystem
def normalize_word(word):
    # Сначала очищаем от знаков препинания
    word = PUNCTUATION_PATTERN.sub('', word.strip())
    lemmas = mystem.lemmatize(word)
    return ''.join(lemmas).strip()


# Расширение запроса пользователя через лемматизацию
def expand_query(query):
    # Очищаем запрос от знаков препинания
    clean_query = PUNCTUATION_PATTERN.sub(' ', query.lower())

    # Разбиваем на слова
    words = clean_query.split()

    # Используем лемматизацию для получения базовой формы слов
    expanded_words = set()
    for word in words:
        # Добавляем исходное слово
        if word:  # проверяем, что слово не пустое после очистки
            expanded_words.add(word)

            # Нормализуем слово и добавляем его лемму
            norm_word = normalize_word(word)
            if norm_word:  # Проверка на пустую строку
                expanded_words.add(norm_word)

    return expanded_words



