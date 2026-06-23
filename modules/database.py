from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# --- МОДЕЛИ ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    history = relationship("MessageHistory", back_populates="user")

class MessageHistory(Base):
    __tablename__ = "message_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="history")

class BitrixDoc(Base):
    __tablename__ = "bitrix_docs"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- ФУНКЦИИ ---
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована.")

def get_or_create_user(tg_id, username, first_name):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            user = User(tg_id=tg_id, username=username, first_name=first_name)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()

def save_interaction(user_id, query, response):
    db = SessionLocal()
    try:
        interaction = MessageHistory(user_id=user_id, query=query, response=response)
        db.add(interaction)
        db.commit()
    finally:
        db.close()

def save_or_update_doc(url: str, title: str, content: str, category: str = "general"):
    db = SessionLocal()
    try:
        doc = db.query(BitrixDoc).filter(BitrixDoc.url == url).first()
        if doc:
            doc.title = title
            doc.content = content
            doc.category = category
            doc.updated_at = datetime.utcnow()
            print(f"🔄 Обновлено в БД: {title}")
        else:
            doc = BitrixDoc(url=url, title=title, content=content, category=category)
            db.add(doc)
            print(f"✅ Сохранено в БД: {title}")
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка БД ({url}): {e}")
        return False
    finally:
        db.close()