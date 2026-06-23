"""
Модуль парсинга документации Bitrix24.
Рекурсивно обходит сайт apidocs.bitrix24.ru, извлекая ссылки и контент.
"""

import sys
import os
import time
from urllib.parse import urljoin, urlparse
from collections import deque

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from config import SELENIUM_HEADLESS
from modules.database import save_or_update_doc, SessionLocal, BitrixDoc

# Начальная страница документации
START_URL = "https://apidocs.bitrix24.ru/api-reference/index.html"
# Домен, в пределах которого парсим (не уходим на внешние сайты)
ALLOWED_DOMAIN = "apidocs.bitrix24.ru"
# Максимальное количество страниц для парсинга (для безопасности)
MAX_PAGES = 20


def setup_driver():
    """Настраивает Chrome WebDriver"""
    options = Options()
    if SELENIUM_HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)


def is_valid_url(url: str) -> bool:
    """Проверяет, что URL относится к документации Bitrix24"""
    parsed = urlparse(url)
    # Только HTTP/HTTPS
    if parsed.scheme not in ('http', 'https'):
        return False
    # Только наш домен
    if ALLOWED_DOMAIN not in parsed.netloc:
        return False
    # Только HTML-страницы (исключаем картинки, JS, CSS)
    path = parsed.path.lower()
    if path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.js', '.css', '.pdf', '.zip')):
        return False
    return True


def extract_links_from_html(html: str, base_url: str) -> list:
    """Извлекает все ссылки со страницы через BeautifulSoup"""
    soup = BeautifulSoup(html, 'lxml')
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Преобразуем относительные ссылки в абсолютные
        full_url = urljoin(base_url, href)
        # Убираем якоря (#section)
        full_url = full_url.split('#')[0]
        if is_valid_url(full_url):
            links.append(full_url)
    return list(set(links))  # Убираем дубликаты


def extract_content(driver, url: str):
    """Извлекает заголовок и контент со страницы"""
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        time.sleep(1.5)
        
        # Получаем HTML через Selenium (с отрендеренным JS)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        
        # Заголовок — из тега h1 или title
        title = ""
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        else:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
        
        # Контент — из основного блока документации
        content = ""
        content_block = soup.find(class_='dc-doc-page__body')
        if content_block:
            content = content_block.get_text(separator='\n', strip=True)
        else:
            # Фолбэк: берём main
            main = soup.find('main')
            if main:
                content = main.get_text(separator='\n', strip=True)
        
        # Чистим от лишних пустых строк
        if content:
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
        
        return title, content, html
    except Exception as e:
        print(f"   ⚠️ Ошибка извлечения контента: {e}")
        return "", "", ""


def get_already_parsed_urls() -> set:
    """Получает список уже спарсенных URL из БД"""
    db = SessionLocal()
    try:
        urls = {doc.url for doc in db.query(BitrixDoc.url).all()}
        return urls
    finally:
        db.close()


def scrape_full_documentation():
    """
    Рекурсивный парсер документации.
    Использует BFS (обход в ширину) для обхода всех страниц.
    """
    print("=" * 70)
    print("🕷️  ЗАПУСК ПОЛНОГО ПАРСИНГА ДОКУМЕНТАЦИИ BITRIX24")
    print("=" * 70)
    print(f"📍 Начальная страница: {START_URL}")
    print(f"🎯 Максимум страниц: {MAX_PAGES}")
    print(f"🌐 Домен: {ALLOWED_DOMAIN}")
    print("=" * 70)
    
    # Получаем уже спарсенные URL (чтобы не парсить заново)
    already_parsed = get_already_parsed_urls()
    print(f"📚 Уже в базе данных: {len(already_parsed)} страниц")
    
    # Очередь для BFS
    queue = deque([START_URL])
    # Множество посещённых URL (защита от зацикливания)
    visited = set(already_parsed)
    
    driver = setup_driver()
    success_count = 0
    error_count = 0
    
    try:
        while queue and len(visited) < MAX_PAGES:
            url = queue.popleft()
            
            # Пропускаем уже посещённые
            if url in visited and url in already_parsed:
                continue
            visited.add(url)
            
            print(f"\n[{len(visited)}/{MAX_PAGES}] 🌐 {url}")
            
            # Извлекаем контент
            title, content, html = extract_content(driver, url)
            
            if not title or not content or len(content) < 100:
                print(f"   ⚠️ Пропускаю (нет контента или слишком короткий)")
                error_count += 1
                continue
            
            # Определяем категорию из URL
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            category = path_parts[-2] if len(path_parts) >= 2 else "general"
            
            # Сохраняем в БД
            try:
                save_or_update_doc(url=url, title=title, content=content, category=category)
                success_count += 1
                print(f"   ✅ Сохранено: {title[:60]}... ({len(content)} символов)")
            except Exception as e:
                print(f"   ❌ Ошибка сохранения: {e}")
                error_count += 1
            
            # Извлекаем ссылки и добавляем в очередь
            if html:
                new_links = extract_links_from_html(html, url)
                new_links = [link for link in new_links if link not in visited]
                if new_links:
                    queue.extend(new_links)
                    print(f"   🔗 Найдено новых ссылок: {len(new_links)} (в очереди: {len(queue)})")
            
            # Небольшая пауза, чтобы не нагружать сервер
            time.sleep(0.5)
    
    finally:
        driver.quit()
    
    # Итоги
    print("\n" + "=" * 70)
    print("🎉 ПАРСИНГ ЗАВЕРШЁН!")
    print("=" * 70)
    print(f"✅ Успешно сохранено: {success_count}")
    print(f"❌ Пропущено с ошибками: {error_count}")
    print(f"📊 Всего обработано URL: {len(visited)}")
    print("=" * 70)


if __name__ == "__main__":
    scrape_full_documentation()