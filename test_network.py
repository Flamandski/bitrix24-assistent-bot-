"""
Скрипт для проверки доступности серверов Telegram API.
Используется для диагностики проблем с сетью.
"""

import requests


def test_telegram_api():
    """Проверяет доступность api.telegram.org"""
    print("=" * 60)
    print("🔍 Проверка доступности Telegram API")
    print("=" * 60)
    
    url = "https://api.telegram.org"
    
    try:
        print(f"\n🌐 Отправляю запрос на {url}...")
        response = requests.get(url, timeout=10)
        print(f"✅ Успех! Статус ответа: {response.status_code}")
        print(f"   Сервер: {response.headers.get('server', 'неизвестно')}")
        return True
    except requests.exceptions.Timeout:
        print(f"❌ ТАЙМАУТ! Сервер не отвечает в течение 10 секунд.")
        print(f"   Возможные причины:")
        print(f"   - Telegram заблокирован вашим провайдером")
        print(f"   - VPN не включён или не работает")
        print(f"   - Проблемы с интернет-соединением")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ ОШИБКА СОЕДИНЕНИЯ!")
        print(f"   Детали: {str(e)[:200]}")
        print(f"   Возможные причины:")
        print(f"   - Нет доступа к интернету")
        print(f"   - Блокировка на уровне провайдера (DPI/SNI)")
        print(f"   - Неправильные настройки прокси")
        return False
    except Exception as e:
        print(f"❌ НЕИЗВЕСТНАЯ ОШИБКА: {type(e).__name__}")
        print(f"   Детали: {str(e)}")
        return False


def test_core_telegram():
    """Проверяет доступность core.telegram.org"""
    print("\n" + "=" * 60)
    print("🔍 Проверка доступности core.telegram.org")
    print("=" * 60)
    
    url = "https://core.telegram.org"
    
    try:
        print(f"\n🌐 Отправляю запрос на {url}...")
        response = requests.get(url, timeout=10)
        print(f"✅ Успех! Статус ответа: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {str(e)[:200]}")
        return False


def main():
    print("\n🛠️  Диагностика сетевого подключения для Telegram-бота\n")
    
    result1 = test_telegram_api()
    result2 = test_core_telegram()
    
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ПРОВЕРКИ")
    print("=" * 60)
    
    if result1 and result2:
        print("✅ Все проверки пройдены! Сеть работает корректно.")
        print("   Можно запускать бота: python main.py")
    elif result1 or result2:
        print("⚠️  Частичная доступность. Telegram может работать нестабильно.")
        print("   Рекомендуется включить VPN.")
    else:
        print("❌ Telegram заблокирован в вашей сети!")
        print("   Решения:")
        print("   1. Включите VPN (Browsec, ProtonVPN, Cloudflare WARP)")
        print("   2. Используйте мобильный интернет (раздача с телефона)")
        print("   3. Настройте прокси в коде бота")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()