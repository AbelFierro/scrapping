import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from constants import *
from helpers import traverseTree

BASE_URL = "https://cabaprop.com.ar"


# 🚀 Inicializa un nuevo driver
def init_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    #options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


# 🧠 Click en la pestaña DETALLES
def click_on_detalles_tab(driver):
    tabs = driver.find_elements(By.CLASS_NAME, "custom-link")
    for tab in tabs:
        if "DETALLES" in tab.text.upper():
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", tab)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tab)
            return True
    return False


# 📄 Extrae detalles de la página activa
def extract_details_from_page(driver):
    time.sleep(1)  # esperar a que cargue el contenido
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    descripcion = soup.find_all('div', class_='row')
    soup = BeautifulSoup(str(descripcion), 'html.parser')
    data = []
    traverseTree(soup, data)
    del data[:5]  # limpieza inicial
    return data


# 🏠 Scrap de la propiedad individual
def scrap_property_detail(url, headless=False):
    extra_data = []
    driver = init_driver(headless=headless)
    try:
        driver.get(url)
        time.sleep(1.5)
        driver.execute_script("window.scrollTo(0, 400);")

        if click_on_detalles_tab(driver):
            print(f"✅ DETALLES abierto en {url}")
            extra_data = extract_details_from_page(driver)
        else:
            print(f"⚠️ No se encontró la pestaña DETALLES en {url}")

    except Exception as e:
        print(f"❌ Error al extraer detalles de {url}: {e}")
    finally:
        driver.quit()

    return extra_data


# 📄 Scrap de la página de resultados (múltiples propiedades)
def scrap_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = soup.find_all(class_=CONTAINER_CLASS)
    page_data_list = []

    for result in results:
        link_tag = result.find('a', href=True)
        if link_tag:
            property_url = BASE_URL + link_tag['href']
            print("🔗 Entrando a:", property_url)
            time.sleep(0.5)
            data = scrap_property_detail(property_url, headless=True)
            #print(data)
            page_data_list.append(data)

    return page_data_list
