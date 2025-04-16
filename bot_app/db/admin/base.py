import os

from bot_app.config import FILES_PATH
from bot_app.db.main import create_dict_con
import pandas as pd


class FAQDatabase:
    @staticmethod
    async def add_faq(answer_ru: str, answer_en: str, questions_ru: list, questions_en: list):
        """Добавляет новый ответ с вопросами в БД."""
        con, cur = await create_dict_con()
        try:
            await cur.execute("INSERT INTO faq (answer_ru, answer_en) VALUES (%s, %s)", (answer_ru, answer_en))
            faq_id = cur.lastrowid

            questions = [(faq_id, q_ru, q_en) for q_ru, q_en in zip(questions_ru, questions_en)]
            await cur.executemany("INSERT INTO faq_questions (faq_id, question_ru, question_en) VALUES (%s, %s, %s)",
                                  questions)

            await con.commit()
        except Exception as e:
            await con.rollback()
            print(f"Ошибка при добавлении FAQ: {e}")
        finally:
            await con.ensure_closed()

    @staticmethod
    async def delete_faq(faq_id: int):
        """Удаляет ответ и связанные с ним вопросы."""
        con, cur = await create_dict_con()
        try:
            await cur.execute("SELECT 1 FROM faq WHERE id = %s", (faq_id,))
            result = await cur.fetchone()

            if not result:
                return False

            await cur.execute("DELETE FROM faq WHERE id = %s", (faq_id,))
            await con.commit()
            return True

        except Exception as e:
            await con.rollback()
            print(f"Ошибка при удалении FAQ: {e}")
            return False
        finally:
            await con.ensure_closed()

    @staticmethod
    async def get_all_questions():
        """Получает все вопросы и ответы из базы данных."""
        con, cur = await create_dict_con()
        try:
            await cur.execute("""
                SELECT f.id as faq_id, f.answer_ru, f.answer_en, q.question_ru, q.question_en
                FROM faq_questions q
                JOIN faq f ON q.faq_id = f.id
            """)
            rows = await cur.fetchall()
            return rows
        except Exception as e:
            print(f"Ошибка при получении вопросов: {e}")
            return []
        finally:
            await con.ensure_closed()

    @staticmethod
    async def get_question_by_id(faq_id: int) -> dict | None:
        con, cur = await create_dict_con()
        try:
            await cur.execute("SELECT * FROM faq WHERE id = %s", (faq_id,))
            result = await cur.fetchone()
            return result
        except Exception as e:
            print(f"Ошибка при получении ответа по ID: {e}")
        finally:
            await con.ensure_closed()

    @staticmethod
    async def get_faq_data_by_language(lang: str, faq_id: int = None) -> list[dict] | None:
        con, cur = await create_dict_con()
        try:
            query = f"""
                SELECT 
                    f.id as faq_id,
                    f.answer_{lang} as answer,
                    q.question_{lang} as question
                FROM faq_questions q
                JOIN faq f ON q.faq_id = f.id
                WHERE q.question_{lang} IS NOT NULL
            """

            if faq_id is not None:
                query += " AND q.faq_id = %s"
                await cur.execute(query, (faq_id,))
            else:
                await cur.execute(query)

            rows = await cur.fetchall()
            return rows

        except Exception as e:
            print(f"Ошибка при получении FAQ на языке {lang}: {e}")
            return None
        finally:
            await con.ensure_closed()


class ExcelOperation:
    @staticmethod
    async def add_xlsx_data(file_name: str):
        # Подключение к БД
        con, cur = await create_dict_con()
        save_path = os.path.join(FILES_PATH, file_name)

        # Загружаем Excel без заголовков
        df = pd.read_excel(save_path, header=None)

        result = []

        # Собираем данные строк
        for row in df.itertuples(index=False, name=None):
            if all(pd.isna(cell) for cell in row):
                break  # Пустая строка — конец данных
            result.append([str(cell).strip() if pd.notna(cell) else "" for cell in row[:4]])

        if not result:
            return False

        # Чистим старые записи
        await cur.execute("DELETE FROM faq_questions")
        await cur.execute("DELETE FROM faq")
        await con.commit()

        for data in result:
            raw_ru = data[0]
            raw_en = data[1]
            answer_ru = data[2]
            answer_en = data[3]

            # Разделяем вопросы по \n и удаляем пустые
            questions_ru = [q.strip() for q in raw_ru.split('\n') if q.strip()]
            questions_en = [q.strip() for q in raw_en.split('\n') if q.strip()]

            # Если хотя бы с одной стороны нет вопросов — пропускаем строку
            if not questions_ru or not questions_en:
                print(f"Пропущена строка — пустые вопросы. RU: {questions_ru}, EN: {questions_en}")
                continue

            # Выравниваем количество вопросов (дублируем, если нужно)
            max_len = max(len(questions_ru), len(questions_en))
            if len(questions_ru) < max_len:
                questions_ru *= max_len
            if len(questions_en) < max_len:
                questions_en *= max_len

            # Вставляем ответ
            await cur.execute("INSERT INTO faq (answer_ru, answer_en) VALUES (%s, %s)", (answer_ru, answer_en))
            faq_id = cur.lastrowid

            # Вставляем пары вопросов
            questions = [(faq_id, q_ru, q_en) for q_ru, q_en in zip(questions_ru, questions_en)]
            await cur.executemany(
                "INSERT INTO faq_questions (faq_id, question_ru, question_en) VALUES (%s, %s, %s)",
                questions
            )
            await con.commit()

        # Удаляем файл после загрузки
        if os.path.exists(save_path):
            os.remove(save_path)
            print(f"Файл {file_name} был успешно удален.")
        return True




# class ExcelOperation:
#     @staticmethod
#     async def add_xlsx_data(file_name: str):
#         # asd = [['Какие есть способы оплаты?\nКак можно оплатить заказ?\nМожно ли оплатить картой?\nКакие формы оплаты вы принимаете?', 'What are the payment methods?\nHow can I pay for the order?\nCan I pay with a card?\nWhat forms of payment do you accept?', 'Оплата возможна картой, банковским переводом или наличными.', 'Payment can be made by card, bank transfer, or cash.'], ['1', '2', '3', '4']]
#         con, cur = await create_dict_con()
#         save_path = os.path.join(FILES_PATH, file_name)
#         df = pd.read_excel(save_path, header=None)
#
#         result = []
#
#         for row in df.itertuples(index=False, name=None):
#             if all(pd.isna(cell) for cell in row):
#                 break
#
#             result.append([str(cell) if pd.notna(cell) else None for cell in row[:4]])
#         if result:
#             await cur.execute("DELETE FROM faq_questions")
#             await cur.execute("DELETE FROM faq")
#             await con.commit()
#             for data in result:
#                 answer_ru = data[-2]
#                 answer_en = data[-1]
#                 questions_data = data[:-2]
#
#                 questions_ru = []
#                 questions_en = []
#
#                 for question_data in questions_data:
#                     for question in question_data.split('\n'):
#                         try:
#                             language = detect(question)
#                             if language == 'ru':
#                                 questions_ru.append(question)
#                             elif language == 'en':
#                                 questions_en.append(question)
#                         except Exception as e:
#                             print(f"Ошибка при определении языка для текста: {question}. Ошибка: {e}")
#                             return False
#
#                 await cur.execute("INSERT INTO faq (answer_ru, answer_en) VALUES (%s, %s)", (answer_ru, answer_en))
#                 faq_id = cur.lastrowid
#                 if len(questions_ru) != len(questions_en):
#                     raise ValueError("Количество вопросов на русском и английском языках не совпадает!")
#
#
#                 questions = [(faq_id, q_ru, q_en) for q_ru, q_en in zip(questions_ru, questions_en)]
#
#                 await cur.executemany("INSERT INTO faq_questions (faq_id, question_ru, question_en) VALUES (%s, %s, %s)",
#                                       questions)
#                 await con.commit()
#
#             if os.path.exists(save_path):
#                 os.remove(save_path)
#                 print(f"Файл {file_name} был успешно удален.")
#             return True
#         else:
#             return False