import os
import time
import json
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🛠️ CONFIGURACIÓN
BASE_URL = "https://mudafy.com.ar"
ZONA_URL = "https://mudafy.com.ar/venta/departamentos/caba-palermo"
OUTPUT_DIR = os.path.expanduser("~/Documentos/Austral/Austral/Web Mining/Trabajo Final/mudafy_large/caba/palermo")
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progreso_palermo.json")
TOTAL_PAGES = 92     # Total de páginas disponibles para Palermo
PAGES_TO_VISIT = 92  # Cambiá esto para limitar las páginas (por ejemplo, 10)
DELAY_BETWEEN_PROPERTIES = (1.5, 3.0)  # Delay en segundos (min, max)
START_PAGE = 80
END_PAGE = 92

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return webdriver.Chrome(options=options)

def save_html(url, content):
    parsed = urlparse(url)
    name = parsed.path.strip("/").replace("/", "_")
    filename = f"detalle_{name}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Guardado: {filename}")

def save_progress(visited_urls):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"visited_urls": list(visited_urls)}, f, indent=2)
    print("💾 Progreso guardado")

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("visited_urls", []))
    return set()

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def run():
    from random import uniform
    driver = get_driver()
    visited_urls = load_progress()

    try:
        for page in range(START_PAGE, END_PAGE + 1):
            url = f"{ZONA_URL}/{page}-p" if page > 1 else ZONA_URL
            print(f"\n📄 Página {page}: {url}")
            driver.get(url)

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h3.location a"))
                )
                scroll_to_bottom(driver)
            except Exception:
                print("⚠️ Timeout esperando la carga")

            links = driver.find_elements(By.CSS_SELECTOR, "h3.location a")
            detail_urls = [urljoin(BASE_URL, a.get_attribute("href")) for a in links]

            print(f"🔗 Propiedades encontradas: {len(detail_urls)}")

            for i, detail_url in enumerate(detail_urls, 1):
                if detail_url in visited_urls:
                    print(f"⏭️ Ya descargada: {detail_url}")
                    continue

                print(f"💾 ({i}/{len(detail_urls)}) Descargando: {detail_url}")
                try:
                    driver.get(detail_url)
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    time.sleep(2)
                    html = driver.execute_script("return document.documentElement.outerHTML;")
                    save_html(detail_url, html)
                    visited_urls.add(detail_url)
                    save_progress(visited_urls)
                except Exception as e:
                    print(f"❌ Error en {detail_url}: {e}")

                time.sleep(uniform(*DELAY_BETWEEN_PROPERTIES))

    finally:
        driver.quit()
        save_progress(visited_urls)
        print("\n🎉 Proceso finalizado")

if __name__ == "__main__":
    run()
