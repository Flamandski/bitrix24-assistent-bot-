import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import asyncio

from modules.database import get_or_create_user, save_interaction
from modules.yandex_assistant import YandexAssistantManager
from config import TELEGRAM_BOT_TOKEN


os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("ALL_PROXY", None)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

assistant = YandexAssistantManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username, user.first_name)
    await update.message.reply_text(f"Привет, {user.first_name}! Я бот-помощник по API Bitrix24. Задай мне вопрос.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    query_text = update.message.text
    
    print(f"\n📨 Получено сообщение от {user.first_name} (@{user.username})")
    print(f"   Текст: {query_text}")
    
    try:
        db_user = get_or_create_user(user.id, user.username, user.first_name)
        print(f"✅ Пользователь найден/создан в БД (ID: {db_user.id})")
        
        await update.message.reply_text("🔍 Ищу информацию в документации...")
        
        session_id = f"tg_user_{user.id}"
        print(f"🤖 Отправляю запрос в YandexGPT (Session: {session_id})...")
        
        response_text = await asyncio.to_thread(
            assistant.send_message, session_id, query_text
        )
        
        print(f"✅ Получен ответ от YandexGPT ({len(response_text)} символов)")
        
        save_interaction(db_user.id, query_text, response_text)
        print(f"✅ Взаимодействие сохранено в БД")
        
        # ⚡ ИСПРАВЛЕНИЕ: убираем parse_mode, чтобы избежать ошибок парсинга Markdown
        await update.message.reply_text(response_text)
        print(f"✅ Ответ отправлен пользователю\n")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке вашего запроса."
        )

def run_bot():
    request = HTTPXRequest(
        proxy=None,
        connect_timeout=30.0,
        read_timeout=30.0
    )
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Бот запущен (системные прокси отключены) и ожидает сообщений...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)