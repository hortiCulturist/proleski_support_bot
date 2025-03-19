from bot_app.db.main import create_dict_con, create_con


class UserDatabase:
    @staticmethod
    async def add_user(user_id: int, name: str, username: str):
        con, cur = await create_con()
        try:
            await cur.execute('SELECT user_id FROM user WHERE user_id = %s', (user_id,))
            result = await cur.fetchone()

            if result:
                return False

            await cur.execute('INSERT INTO user (user_id, name, username) VALUES (%s, %s, %s)',
                              (user_id, name, username))
            await con.commit()
            return True
        finally:
            await con.ensure_closed()

    @staticmethod
    async def get_user(user_id: int):
        con, cur = await create_dict_con()
        try:
            await cur.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
            result = await cur.fetchone()
            return result
        finally:
            await con.ensure_closed()

    @staticmethod
    async def save_user_phone(phone_number: str, user_id: int):
        con, cur = await create_dict_con()
        try:
            await cur.execute('UPDATE user SET phone = %s WHERE user_id = %s', (phone_number, user_id))
        finally:
            await con.ensure_closed()

    @staticmethod
    async def edit_language(user_id: int, language: str):
        con, cur = await create_dict_con()
        try:
            await cur.execute('UPDATE user SET language = %s WHERE user_id = %s', (language, user_id))
            await con.commit()
        finally:
            await con.ensure_closed()


# async def add_user( user_id: int, name: str, username: str):
#     con, cur = await create_con()
#     try:
#         await cur.execute('SELECT user_id FROM user WHERE user_id = %s', (user_id,))
#         result = await cur.fetchone()
#
#         if result:
#             return False
#
#         await cur.execute('INSERT INTO user (user_id, name, username) VALUES (%s, %s, %s)',
#                           (user_id, name, username))
#         await con.commit()
#         return True
#     finally:
#         await con.ensure_closed()