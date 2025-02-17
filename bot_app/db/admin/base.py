from bot_app.db.main import create_dict_con


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
