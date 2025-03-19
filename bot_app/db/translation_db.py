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
