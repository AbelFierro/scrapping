import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#from constants import *
from helpers import traverseTree

BASE_URL = "https://www.argenprop.com"
CONTAINER_CLASS = "listing__item"  # Ajustar según HTML real

def init_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def extract_details_from_page(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "property-features"))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    detalles = []
   
    #property-features
    # Extraer dirección
    #sections = soup.find_all('ul', class_='property-features')
    
    direccion_tag = soup.find('h2', class_='titlebar__address')
    if direccion_tag:
        direccion = direccion_tag.get_text(strip=True)
        detalles.append(f"Dirección:{direccion}")
        print(f"📍 Dirección encontrada: {direccion}")

    sections = soup.find_all('ul', class_='property-features')
    for ul in sections:
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            if text and text != "$0":
                detalles.append(text)
                #print(detalles)
    return detalles

def scrap_property_detail(url, headless=False):
    detalles = []
    driver = init_driver(headless=headless)
    try:
        driver.get(url)
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 400);")
        detalles = extract_details_from_page(driver)
        print(detalles)
    except Exception as e:
        print(f"❌ Error al extraer detalles de {url}: {e}")
    finally:
        driver.quit()
    return detalles

def scrap_page_argen(html_content):
    #print("pasa por aca")
    soup = BeautifulSoup(html_content, 'html.parser')
    results = soup.find_all(class_=CONTAINER_CLASS)
    page_data_list = []

    for result in results:
        link_tag = result.find('a', href=True)
        if link_tag:
            property_url = BASE_URL + link_tag['href']
            print(property_url)
            print("🔗 Entrando a:", property_url)
            time.sleep(0.5)
            data = scrap_property_detail(property_url)
            #print(data)
            page_data_list.append(data)

    return page_data_list