from bot_app.db.main import create_dict_con, create_con

class TranslationDB:
    @staticmethod
    async def get_translation(user_id: int, key_name: str, default_lang: str = None):
        con, cur = await create_dict_con()
        try:
            # Если язык не передан, получаем его из БД
            if default_lang is None:
                await cur.execute('SELECT `language` FROM `user` WHERE `user_id` = %s', (user_id,))
                user_info = await cur.fetchone()
                default_lang = user_info['language'] if user_info else 'en'  # Можно задать язык по умолчанию

            # Ищем перевод в базе
            await cur.execute(
                'SELECT `value` FROM `base_translation` WHERE `lang` = %s AND `key_name` = %s LIMIT 1',
                (default_lang, key_name)
            )
            translation = await cur.fetchone()

            return translation.get('value') if translation else None
        finally:
            await con.ensure_closed()

    @staticmethod
    async def get_user_language_code(user_id: int):
        con, cur = await create_dict_con()
        await cur.execute('SELECT `language` FROM `user` WHERE `user_id` = %s', (user_id,))
        user_lang_code = await cur.fetchone()
        return user_lang_code["language"]

    @staticmethod
    async def get_admin_translation(user_id: int, key_name: str, default_lang: str = None):
        con, cur = await create_dict_con()
        try:
            # Если язык не передан, получаем его из БД
            if default_lang is None:
                await cur.execute('SELECT `language` FROM `user` WHERE `user_id` = %s', (user_id,))
                user_info = await cur.fetchone()
                default_lang = user_info['language'] if user_info else 'en'  # Можно задать язык по умолчанию

            # Ищем перевод в базе
            await cur.execute(
                'SELECT `value` FROM `admin_translation` WHERE `lang` = %s AND `key_name` = %s LIMIT 1',
                (default_lang, key_name)
            )
            translation = await cur.fetchone()

            return translation.get('value') if translation else None
        finally:
            await con.ensure_closed()

    @staticmethod
    async def add_admin_translation(key_name: str, ru_text: str, en_text: str):
        con, cur = await create_dict_con()
        try:
            await cur.execute("DELETE FROM admin_translation WHERE key_name = %s", (key_name,))
            await cur.execute('INSERT INTO admin_translation (lang, key_name, value) VALUES (%s, %s, %s)',
                              ("ru", key_name, ru_text))
            await cur.execute('INSERT INTO admin_translation (lang, key_name, value) VALUES (%s, %s, %s)',
                              ("en", key_name, en_text))
            await con.commit()
        finally:
            await con.ensure_closed()














