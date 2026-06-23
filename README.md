# 🤖 Telegram-бот помощник по API Bitrix24 на базе YandexGPT с RAG

Интеллектуальный чат-бот для разработчиков, отвечающий на вопросы по официальной документации REST API Bitrix24. Использует LLM **YandexGPT** и технологию **RAG (Retrieval-Augmented Generation)** с **векторным поиском FAISS** для семантического поиска точных ответов в актуальной базе знаний.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![YandexGPT](https://img.shields.io/badge/YandexGPT-5-red?logo=yandex)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-purple)
![RAG](https://img.shields.io/badge/RAG-Architecture-orange)

## ✨ Возможности

- 💬 Отвечает на вопросы по API Bitrix24 на естественном языке
- 🧠 **RAG с векторным поиском FAISS** — семантический поиск релевантной документации
- 📚 Использует актуальную документацию с `apidocs.bitrix24.ru` в качестве базы знаний
- 🤖 Обработка запросов через YandexGPT 5 (Foundation Models API)
- 🕷️ **Рекурсивный парсер** документации через Selenium с обходом по ссылкам
- 🗄️ Хранение данных в PostgreSQL через SQLAlchemy ORM
- 📊 Ведение истории взаимодействий с пользователями
- 🔒 Безопасное хранение секретов через `.env`
- ⚡ Асинхронная обработка сообщений без блокировки event loop

## 🛠️ Технологический стек

| Технология | Версия | Назначение |
|---|---|---|
| **Python** | **3.13** | Основной язык разработки |
| python-telegram-bot | 21.9 | Интеграция с Telegram Bot API |
| SQLAlchemy | ≥2.0.35 | ORM для работы с PostgreSQL |
| psycopg[binary] | 3.x | Драйвер PostgreSQL |
| python-dotenv | 1.0.1 | Загрузка переменных окружения |
| Selenium | 4.18.1 | Парсинг динамических веб-страниц |
| requests | 2.31.0 | HTTP-запросы к YandexGPT API |
| **FAISS** | ≥1.9.0 | **Векторный поиск для RAG** |
| **sentence-transformers** | ≥2.5.0 | **Модель эмбеддингов (all-MiniLM-L6-v2)** |
| **torch** | ≥2.0.0 | Фреймворк для нейросетей |
| BeautifulSoup4 | ≥4.12.0 | Парсинг HTML при рекурсивном обходе |
| lxml | ≥5.0.0 | Быстрый HTML-парсер |
| PostgreSQL | 16 | Реляционная база данных |
| YandexGPT | latest | LLM для генерации ответов |

> ⚠️ **Важно:** Проект протестирован на **Python 3.13**. Использование Python 3.14 или ниже 3.12 может вызвать проблемы совместимости с библиотеками SQLAlchemy и psycopg.

## 📁 Структура проекта

```
bitrix24-assistant-bot/
│
├── .env                    # Секретные данные (НЕ загружается в git)
├── .gitignore              # Исключения для git
├── requirements.txt        # Зависимости Python
├── README.md               # Документация проекта
├── config.py               # Загрузка переменных окружения
├── main.py                 # Точка входа (оркестратор)
├── create_tables.py        # Скрипт инициализации БД
├── rebuild_index.py        # Перестроение FAISS-индекса
├── test_network.py         # Диагностика сетевого подключения
│
└── modules/
    ├── __init__.py
    ├── database.py         # Модуль БД (SQLAlchemy, модели, CRUD)
    ├── scraper.py          # Рекурсивный парсинг документации (Selenium + BFS)
    ├── rag.py              # Модуль RAG (FAISS + эмбеддинги)
    ├── yandex_assistant.py # Модуль интеграции с YandexGPT
    └── telegram_bot.py     # Модуль интеграции с Telegram (async)
```

## 💻 Системные требования

- **Python 3.13** (рекомендуется)
- **PostgreSQL 16** (или новее)
- **Google Chrome** (для работы Selenium)
- **Учётная запись Yandex Cloud** с доступом к YandexGPT API
- **Telegram-бот**, созданный через [@BotFather](https://t.me/BotFather)
- **Минимум 4 ГБ свободной ОЗУ** (для работы модели эмбеддингов)

## 🚀 Установка и запуск

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Flamandski/bitrix24-assistant-bot.git
cd bitrix24-assistant-bot
```

### Шаг 2: Создание виртуального окружения (venv)

Создайте изолированное Python-окружение для проекта:

**Windows (PowerShell):**
```powershell
# Создаём виртуальное окружение на базе Python 3.13
py -3.13 -m venv venv

# Активируем окружение
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
py -3.13 -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3.13 -m venv venv
source venv/bin/activate
```

**Visual Studio Code (VS Code):**

VS Code предоставляет удобную интеграцию с виртуальными окружениями. Для корректной работы выполните следующие шаги:

1. **Откройте проект в VS Code:**
   ```bash
   code .
   ```
   Или через меню: `File` → `Open Folder...` → выберите папку проекта.

2. **Установите расширение Python** (если ещё не установлено):
   - Откройте панель расширений (`Ctrl+Shift+X`)
   - Найдите и установите официальное расширение **Python** от Microsoft

3. **Создайте виртуальное окружение** через встроенный терминал VS Code (`Ctrl+Shift+` или `View` → `Terminal`):
   ```powershell
   py -3.13 -m venv venv
   ```
   > 💡 Альтернатива: используйте палитру команд (`Ctrl+Shift+P`) → **Python: Create Environment** → выберите `Venv` → укажите интерпретатор Python 3.13. VS Code создаст окружение автоматически.

4. **Активируйте окружение в терминале VS Code:**
   - Windows (PowerShell): `venv\Scripts\Activate.ps1`
   - Windows (CMD): `venv\Scripts\activate.bat`
   - Linux / macOS: `source venv/bin/activate`
   
   > 💡 VS Code обычно автоматически активирует venv при открытии нового терминала, если он был обнаружен в папке проекта.

5. **Выберите интерпретатор Python:**
   - Нажмите `Ctrl+Shift+P` (или `Cmd+Shift+P` на macOS)
   - Введите команду: **`Python: Select Interpreter`**
   - Выберите из списка интерпретатор с путём, содержащим `venv`:
     ```
     Python 3.13.x ('venv': venv) C:\...\bitrix24-assistant-bot\venv\Scripts\python.exe
     ```
   - Если интерпретатор не найден, нажмите **Enter interpreter path...** → **Find...** и укажите путь вручную:
     - Windows: `venv\Scripts\python.exe`
     - Linux / macOS: `venv/bin/python`

6. **Проверьте активацию:**
   - В правом нижнем углу VS Code должно отображаться название выбранного интерпретатора (например, `Python 3.13.x ('venv')`)
   - В терминале должна появиться приставка `(venv)` в начале строки

> ⚠️ **Важно:** Если VS Code выдаёт ошибку `cannot be loaded because running scripts is disabled on this system` при активации через PowerShell, выполните в терминале с правами администратора:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> После этого перезапустите терминал VS Code и повторите активацию.

> 💡 После выбора интерпретатора в VS Code автоматически настраиваются автодополнение кода, подсветка синтаксиса и линтинг для всех библиотек, установленных в виртуальном окружении.

> 💡 После активации в начале строки терминала появится префикс `(venv)`.

### Шаг 3: Установка зависимостей

```bash
# Обновляем pip
python -m pip install --upgrade pip

# Устанавливаем все зависимости из requirements.txt
pip install -r requirements.txt
```

> ⚡ **Ускоренная установка PyTorch** (если зависнет):
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cpu
> pip install faiss-cpu sentence-transformers beautifulsoup4 lxml
> ```

### Шаг 4: Установка и настройка PostgreSQL

1. Скачайте PostgreSQL с официального сайта: https://www.postgresql.org/download/windows/
2. При установке задайте пароль для пользователя `postgres` (запомните его!)
3. Откройте **pgAdmin 4** (устанавливается вместе с PostgreSQL)
4. Создайте новую базу данных:
   - Правой кнопкой по **Databases** → **Create** → **Database...**
   - Имя: `bitrix_bot_db`
   - Owner: `postgres`
   - Нажмите **Save**

### Шаг 5: Получение токенов и ID

#### Telegram Bot Token
1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`, следуйте инструкциям
3. Скопируйте полученный токен

#### Yandex Cloud IAM Token
1. Получите OAuth-токен: https://oauth.yandex.ru/authorize?response_type=token&client_id=1a6990aa636648e9b2ef855fa7bec2fb
2. Обменяйте его на IAM-токен (живёт 12 часов):
   ```bash
   curl -X POST https://iam.api.cloud.yandex.net/iam/v1/tokens \
        -d '{"yandexPassportOauthToken":"ВАШ_OAUTH_TOKEN"}'
   ```
3. Скопируйте значение `iamToken` из ответа
4. В консоли Yandex Cloud (https://console.cloud.yandex.ru/) найдите **Folder ID** (начинается на `b1g`)

### Шаг 6: Создание файла `.env`

В корне проекта создайте файл `.env` и заполните его по шаблону ниже.

### Шаг 7: Инициализация базы данных

```bash
python create_tables.py
```

Этот скрипт создаст в PostgreSQL три таблицы: `users`, `message_history`, `bitrix_docs`.

### Шаг 8: Парсинг документации

Наполните базу знаний документацией с сайта Bitrix24. Парсер работает **рекурсивно** — начиная с одной страницы, он обходит все связанные ссылки:

```bash
python -m modules.scraper
```

⏱️ Полный парсинг занимает 30-60 минут (500 страниц). Для быстрой проверки можно временно установить `MAX_PAGES = 20` в `modules/scraper.py`.

После выполнения в таблице `bitrix_docs` появятся статьи с документацией.

### Шаг 9: Построение FAISS-индекса

Создайте векторный индекс для семантического поиска по документации:

```bash
python rebuild_index.py
```

Ожидаемый вывод:
```
🧠 Загрузка модели эмбеддингов: all-MiniLM-L6-v2...
✅ Модель загружена
🔨 Построение FAISS-индекса из N документов...
✅ FAISS-индекс построен: N векторов, размерность 384
```

> 💡 Модель `all-MiniLM-L6-v2` (~80 МБ) скачивается один раз и сохраняется в кэше `~/.cache/huggingface/`. При следующих запусках она загружается мгновенно.

### Шаг 10: Запуск бота

```bash
python main.py
```

Ожидаемый вывод:
```
✅ Переменные окружения загружены из .env
✅ YandexGPT инициализирован (прямой режим + RAG с FAISS)
🚀 Запуск Bitrix24 Assistant Bot...
✅ База данных инициализирована.
✅ FAISS-индекс загружен: N векторов
🤖 Бот запущен и ожидает сообщений...
```

## 🔐 Описание файла `.env`

Для работы проекта необходимо создать файл `.env` в корне проекта и заполнить его следующими переменными:

| Переменная | Описание | Пример |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота от [@BotFather](https://t.me/BotFather) | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `POSTGRES_USER` | Имя пользователя PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Пароль от PostgreSQL | `my_secure_password` |
| `POSTGRES_DB` | Название базы данных | `bitrix_bot_db` |
| `POSTGRES_HOST` | Хост базы данных | `localhost` |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `YANDEX_OAUTH_TOKEN` | OAuth-токен Яндекс (для получения IAM) | `y0_AgAAAA...` |
| `YANDEX_IAM_TOKEN` | IAM-токен Яндекс Cloud (живёт 12 часов) | `t1.9euelZqZj5q...` |
| `YANDEX_FOLDER_ID` | ID каталога (folder) в Yandex Cloud | `b1gxxxxxxxxxxxxxxx` |
| `SELENIUM_HEADLESS` | Запускать браузер Chrome в фоновом режиме | `True` |

### Пример заполнения `.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=MySecretPassword123
POSTGRES_DB=bitrix_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Yandex Cloud
YANDEX_OAUTH_TOKEN=y0_AgAAAAA...
YANDEX_IAM_TOKEN=t1.9euelZqZj5qPk5iSkZqQj42MkZqN8_...
YANDEX_FOLDER_ID=b1g1234567890abcdef

# Selenium
SELENIUM_HEADLESS=True
```

> ⚠️ **Никогда не загружайте файл `.env` в публичный репозиторий!** Он уже добавлен в `.gitignore`.

## 📖 Использование

После запуска бота откройте Telegram и найдите своего бота по нику.

### Доступные команды:
- `/start` — приветствие и краткая инструкция

### Примеры запросов:
```
Как создать новый контакт в CRM?
Какие параметры нужны для метода crm.contact.add?
Как добавить клиента с телефоном?  # семантический поиск через FAISS
Как получить контакт по ID?
Покажи пример кода для создания контакта
```

> 💡 Благодаря **векторному поиску FAISS**, бот понимает смысл запроса. Например, на вопрос *"Как добавить клиента с телефоном?"* бот найдёт документацию по методу `crm.contact.add`, даже если в запросе нет точного названия метода.

### Обновление базы знаний:
```bash
# 1. Парсим новые страницы документации
python -m modules.scraper

# 2. Перестраиваем FAISS-индекс
python rebuild_index.py

# 3. Запускаем бота
python main.py
```

## 🧪 Тестирование

Для проверки работоспособности выполните:

```bash
# Тест подключения к Telegram API
python test_network.py

# Тест парсинга документации
python -m modules.scraper

# Тест работы FAISS-индекса
python rebuild_index.py

# Проверка количества документов в БД
python -c "from modules.database import SessionLocal, BitrixDoc; db = SessionLocal(); print(f'Документов: {db.query(BitrixDoc).count()}'); db.close()"
```

## 📝 Обоснование выбора технологий

### Почему FAISS и sentence-transformers для RAG?
FAISS — это библиотека векторного поиска от Meta, обеспечивающая миллисекундный поиск по миллионам векторов. Модель `all-MiniLM-L6-v2` от sentence-transformers преобразует текст в 384-мерные векторы эмбеддингов, сохраняя семантическое сходство. Это позволяет боту находить релевантные документы даже при отсутствии точного совпадения ключевых слов.

**Возникшие проблемы:** Библиотека `torch` (зависимость sentence-transformers) весит около 700 МБ и долго устанавливается. Решением стала установка CPU-версии с официального сайта PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`.

### Почему YandexGPT напрямую (без Assistants API)?
Прямой вызов YandexGPT через Foundation Models API даёт полный контроль над формированием контекста, позволяет хранить базу знаний в собственной PostgreSQL (независимость от вендора), обеспечивает мгновенный SQL-поиск по документации и использует ту же модель YandexGPT 5.

**Возникшие проблемы:** Новые OAuth-токены (после июня 2026 года) не поддерживают автоматический обмен на IAM-токен, что потребовало ручного обмена через curl. Также IAM-токен имеет срок жизни 12 часов и требует периодического обновления.
