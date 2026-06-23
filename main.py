from modules.rag import get_rag_searcher

def main():
    # Инициализируем БД
    from modules.database import init_db
    init_db()
    
    # Строим/загружаем FAISS-индекс
    rag = get_rag_searcher()
    if not rag.load_index():
        print("⚠️ FAISS-индекс не найден. Строим новый...")
        rag.build_index()
    
    # Запускаем бота
    from modules.telegram_bot import run_bot
    print("🚀 Запуск Bitrix24 Assistant Bot...")
    run_bot()

if __name__ == "__main__":
    main()