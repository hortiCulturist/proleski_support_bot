# bot_app/utils/neural_search.py

import torch
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict, Optional
import os
import numpy as np

from bot_app.db.admin.base import FAQDatabase
from bot_app.config import PUNCTUATION_PATTERN

# Глобальные переменные для хранения модели и эмбеддингов
model = None
cached_embeddings = {}
faq_data = {}


class NeuralSearch:
    @staticmethod
    async def load_model(model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """Загружает модель трансформера для семантического поиска"""
        global model
        if model is None:
            print(f"Загрузка модели {model_name}...")
            model = SentenceTransformer(model_name)
            print(f"Модель {model_name} успешно загружена.")
        return model

    @staticmethod
    async def precompute_embeddings(lang: str):
        """Предварительная загрузка и вычисление эмбеддингов для всех вопросов"""
        global model, cached_embeddings, faq_data

        # Загрузка модели, если она еще не загружена
        if model is None:
            await NeuralSearch.load_model()

        # Получение всех вопросов для указанного языка
        print(f"Загрузка вопросов на {lang} языке из базы данных...")
        rows = await FAQDatabase.get_faq_data_by_language(lang)

        if not rows:
            print(f"Вопросы на языке {lang} не найдены")
            return False

        # Очистка ранее сохраненных эмбеддингов для этого языка
        if lang in cached_embeddings:
            del cached_embeddings[lang]

        cached_embeddings[lang] = {}
        faq_data[lang] = {}

        # Подготовка текстов и ID для векторизации
        texts = []
        faq_ids = []

        for row in rows:
            question_text = row['question'].strip().lower()
            # Очищаем от знаков препинания
            clean_question = PUNCTUATION_PATTERN.sub(' ', question_text)

            texts.append(clean_question)
            faq_ids.append(row['faq_id'])

            # Сохраняем связь между текстами и ID
            faq_data[lang][clean_question] = row['faq_id']

        # Вычисление эмбеддингов
        print(f"Вычисление эмбеддингов для {len(texts)} вопросов...")
        embeddings = model.encode(texts, convert_to_tensor=True)

        # Сохранение эмбеддингов в кэше
        for text, embedding, faq_id in zip(texts, embeddings, faq_ids):
            cached_embeddings[lang][text] = {
                'embedding': embedding,
                'faq_id': faq_id
            }

        print(f"Предварительная обработка эмбеддингов для {lang} завершена.")
        return True

    @staticmethod
    async def find_similar_questions(query: str, lang: str, limit: int = 6, threshold: float = 0.6) -> List[
        Tuple[str, int, float]]:
        """
        Находит похожие вопросы с использованием семантического поиска.

        Args:
            query: Текст запроса пользователя
            lang: Язык запроса ('ru' или 'en')
            limit: Максимальное количество результатов
            threshold: Минимальный порог сходства (0-1)

        Returns:
            Список кортежей (текст_вопроса, id_вопроса, степень_сходства)
        """
        global model, cached_embeddings, faq_data

        # Загрузка модели, если она еще не загружена
        if model is None:
            await NeuralSearch.load_model()

        # Проверяем, загружены ли эмбеддинги для данного языка
        if lang not in cached_embeddings or not cached_embeddings[lang]:
            print(f"Эмбеддинги для языка {lang} не найдены. Выполняем предварительную обработку...")
            await NeuralSearch.precompute_embeddings(lang)

        # Очищаем и подготавливаем запрос
        clean_query = PUNCTUATION_PATTERN.sub(' ', query.strip().lower())

        # Получаем эмбеддинг запроса
        query_embedding = model.encode(clean_query, convert_to_tensor=True)

        # Вычисляем сходство с каждым вопросом
        results = []

        for question_text, data in cached_embeddings[lang].items():
            question_embedding = data['embedding']
            faq_id = data['faq_id']

            # Косинусное сходство между векторами
            with torch.no_grad():
                cosine_similarity = torch.nn.functional.cosine_similarity(
                    query_embedding.unsqueeze(0),
                    question_embedding.unsqueeze(0)
                ).item()

            if cosine_similarity >= threshold:
                # Сохраняем оригинальный текст вопроса из faq_data
                original_questions = [q for q in faq_data[lang].keys() if faq_data[lang][q] == faq_id]
                if original_questions:
                    results.append((original_questions[0], faq_id, cosine_similarity))

        # Сортируем по убыванию сходства и ограничиваем количество
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]


# Функция для тестирования
async def test_neural_search():
    search = NeuralSearch()
    await search.load_model()

    # Предварительно загрузим эмбеддинги для русского языка
    await search.precompute_embeddings('ru')

    # Тестовые запросы
    test_queries = [
        "Как оплатить?",
        "Сколько стоит тренажер?",
        "Когда будет доставка?"
    ]

    for query in test_queries:
        print(f"\nЗапрос: {query}")
        results = await search.find_similar_questions(query, 'ru', limit=3)

        if results:
            print("Найденные вопросы:")
            for i, (question, faq_id, score) in enumerate(results, 1):
                print(f"{i}. {question} (ID: {faq_id}, сходство: {score:.2f})")
        else:
            print("Подходящих вопросов не найдено.")


# При импорте модуля будет автоматически запущена загрузка модели
if __name__ == "__main__":
    import asyncio

    asyncio.run(test_neural_search())