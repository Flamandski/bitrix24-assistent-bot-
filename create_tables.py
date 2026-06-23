from modules.database import init_db, engine, Base
from modules.database import User, MessageHistory, BitrixDoc  

def force_create_tables():
    print("🔧 Принудительное создание/проверка таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Готово! Таблица bitrix_docs теперь существует.")

if __name__ == "__main__":
    force_create_tables()