"""
Модуль интеграции с YandexGPT через Foundation Models API.
Использует RAG (Retrieval-Augmented Generation) с векторным поиском через FAISS.
"""

import requests
from config import YANDEX_IAM_TOKEN, YANDEX_FOLDER_ID
from modules.rag import get_rag_searcher


class YandexAssistantManager:
    def __init__(self):
        self.iam_token = YANDEX_IAM_TOKEN
        self.folder_id = YANDEX_FOLDER_ID
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        if not self.iam_token:
            raise Exception("❌ YANDEX_IAM_TOKEN не указан в .env!")
        if not self.folder_id:
            raise Exception("❌ YANDEX_FOLDER_ID не указан в .env!")
        
        # Инициализируем RAG-поисковик (FAISS + эмбеддинги)
        self.rag = get_rag_searcher()
        print("✅ YandexGPT инициализирован (прямой режим + RAG с FAISS)")

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.iam_token}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json"
        }

    def send_message(self, session_id, text_query):
        """Отправляет запрос в YandexGPT с контекстом из RAG (FAISS)"""
        
        # 1. Векторный поиск релевантной документации через FAISS
        print(f"🔍 RAG-поиск по запросу: {text_query}")
        context = self.rag.get_context(text_query, top_k=3)
        
        # 2. Формируем промпт с системной инструкцией и контекстом
        system_prompt = """Ты — эксперт по API Bitrix24. Отвечай на вопросы разработчиков, 
опираясь на предоставленную документацию. Будь точным, кратким и полезным. 
Если не знаешь ответа или документации недостаточно — честно скажи об этом.
Всегда указывай ссылку на источник, если он есть в документации."""

        user_message = f"""Контекст из документации Bitrix24 (найден через векторный поиск FAISS):

{context}

---

Вопрос пользователя: {text_query}

Ответь на вопрос, используя ТОЛЬКО информацию из документации выше. 
Если в документации нет ответа — честно скажи об этом."""

        # 3. Формируем запрос к YandexGPT API
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": system_prompt
                },
                {
                    "role": "user",
                    "text": user_message
                }
            ]
        }
        
        # 4. Отправляем запрос
        print(f"🤖 Отправляю запрос в YandexGPT...")
        response = requests.post(
            self.api_url,
            json=payload,
            headers=self._get_headers(),
            timeout=60.0
        )
        
        # 5. Обрабатываем ответ
        if response.status_code == 200:
            data = response.json()
            try:
                answer = data["result"]["alternatives"][0]["message"]["text"]
                print(f"✅ Получен ответ от YandexGPT ({len(answer)} символов)")
                return answer
            except (KeyError, IndexError) as e:
                print(f"❌ Ошибка парсинга ответа: {e}")
                print(f"   Полный ответ: {data}")
                return "Не удалось получить ответ от YandexGPT."
        else:
            print(f"❌ YandexGPT API Error: {response.status_code}")
            print(f"   Ответ: {response.text[:500]}")
            return "Произошла ошибка при обращении к YandexGPT."