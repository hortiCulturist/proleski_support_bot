import asyncio
import os
from typing import Optional, Tuple

import aiomysql
from aiomysql import connect, Connection, Cursor, DictCursor
from pymysql import connect as sync_connect
from rapidfuzz import process
from dotenv import load_dotenv

load_dotenv()

MYSQL = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'db': os.getenv('MYSQL_DB_NAME'),
    'port': int(os.getenv('MYSQL_PORT'))
}

async def create_con():
    con: Connection = await connect(**MYSQL)
    cur: Cursor = await con.cursor()
    return con, cur


async def create_dict_con():
    try:
        con: Connection = await connect(**MYSQL)
        cur: DictCursor = await con.cursor(DictCursor)
        return con, cur
    except Exception as e:
        print(f"Ошибка при подключении к БД: {e}")
        return None, None



class QuestionProcessor:
    def __init__(self, rows):
        self.rows = rows

    def find_best_match(self, user_question: str, lang: str = "ru"):
        column = f"question_{lang}"
        answer_column = f"answer_{lang}"

        questions = [row[column] for row in self.rows if row[column]]

        best_match = process.extractOne(user_question, questions, score_cutoff=70)

        if best_match:
            for row in self.rows:
                if row[column] == best_match[0]:
                    return row[answer_column]
        return None