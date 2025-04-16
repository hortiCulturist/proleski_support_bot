import os
from dotenv import load_dotenv

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