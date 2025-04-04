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
