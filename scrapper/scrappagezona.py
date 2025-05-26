import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

BASE_URL = "https://www.zonaprop.com.ar"
CONTAINER_CLASS = "postingCardLayout-module__posting-card-container"  # Ajustar según HTML real

def init_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def oper_price(input_string):
    # Lista de palabras clave de monedas
    currencies = ['USD', 'ARS', 'EUR']   
    # Inicializar variables
    oper = input_string
    price = ''
    # Buscar la primera moneda que aparezca en la cadena
    for currency in currencies:
        if currency in input_string:
            index = input_string.find(currency)
            oper = input_string[:index].strip()
            price = input_string[index:].strip()
            break
    
    return oper, price

def extract_info(input_string):
    # Formas posibles de expresar metros cuadrados
    forms = ['m²', 'm2', 'metros cuadrados']
    # Buscar la primera forma que aparezca en la cadena
    for form in forms:
        index = input_string.find(form)
        if index != -1:
            return input_string[:index + len(form)].strip()
    # Si no se encuentra ninguna forma, extraer solo los caracteres numéricos del 1 al 9
    numeric_characters = re.findall(r'[1-9]', input_string)
    if numeric_characters:
        return ''.join(numeric_characters)
    # Si la cadena original es 'A estrenar', devolver '0'
    if input_string.strip() == 'A estrenar':
        return '0'
    # Si no se encuentra ninguna forma ni caracteres numéricos, devolver la cadena original
    return input_string.strip()

def extract_details_from_page(driver, url):
     
    detalles = []

    # Extraer datos de geolocalización    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'static-map'))
    )    
    
    try:
        img_element = driver.find_element(By.CSS_SELECTOR, 'img.static-map')
        src = img_element.get_attribute('src')        
        import re
        match = re.search(r'markers=(-?\d+\.\d+),(-?\d+\.\d+)', src)
        if match:
            latitude = match.group(1)
            longitude = match.group(2)
            detalles.append(f'{latitude}, {longitude}')
            print(detalles)
        else:
            print("No se encontraron coordenadas en el atributo 'src'.")
    except:
        pass

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "section-icon-features-property"))
    )
    
    # Título desde Selenium directamente
    try:
        titulo = driver.find_element(By.CLASS_NAME, "title-type-sup-property").text.strip()
        detalles.append(titulo)   #Este puede omitirse porque la dirección no está en ese container 
    except:
        pass
    
    # Extraer datos de iconos (cambia el enfoque a BeautifulSoup para evitar problemas con Selenium)
    from crawler import SeleniumGetHTML
    html_content = SeleniumGetHTML(url)    
    soup = BeautifulSoup(html_content, 'html.parser')
    icon_features = soup.find_all('li', class_='icon-feature')
    
    for feature in icon_features:
        # Encuentra el elemento i (el ícono)
        icon = feature.find('i')
    
        if icon:
            # Identifica el ícono por su clase
            icon_class = icon.get('class')
            icon_identifier = icon_class[0] if icon_class else "unknown-icon"
        
            # Obtiene todo el texto del elemento li y elimina cualquier texto dentro del ícono
            full_text = feature.get_text().strip()
        
            # Elimina el texto del ícono del texto completo
            feature_text = re.sub(r'\s+', ' ', full_text).strip()
            clean_text = extract_info(feature_text)
            detalles.append(f"{icon_identifier}: {clean_text}")
            print(f"{icon_identifier}: {clean_text}")

    # Extraer calle-altura
    try:
        calle_altura = soup.find_all('h4')[1].text.strip()
        # Buscar la posición de la primera coma
        index = calle_altura.find(',')
        if index != -1:
            # Devolver todo lo que está a la izquierda de la coma, sin incluirla
            calle_altura_sin_coma = calle_altura[:index].strip()
        else:
            # Si no hay coma, devolver el texto original
            calle_altura_sin_coma = calle_altura.strip()
            
        detalles.append(calle_altura_sin_coma)
    except:
        pass

    # Extraer operación-precio    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'price-container-property'))
    )    

    try:
        oper_price_element = driver.find_element(By.CLASS_NAME, 'price-value')
        oper_precio = oper_price_element.text.strip()
        operacion, price = oper_price(oper_precio)
        detalles.append(operacion)  
        detalles.append(price)
        print(detalles)
    except:
        pass
    
    return detalles

def scrap_property_detail(url, headless=False):
    detalles = []
    driver = init_driver(headless=headless)
    try:
        driver.get(url)
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 400);")
        detalles = extract_details_from_page(driver, url)
        print(detalles)
    except Exception as e:
        print(f"❌ Error al extraer detalles de {url}: {e}")
    finally:
        driver.quit()
    return detalles

def scrap_page_zona(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = soup.find_all(class_=CONTAINER_CLASS)
    # results = results[0] # Solo el primer contenedor
    page_data_list = []

    for result in results:
        link_tag = result.find('a', href=True)
        if link_tag:
            property_url = BASE_URL + link_tag['href']
            print(property_url)
            print("🔗 Entrando a:", property_url)
            time.sleep(1)
            data = scrap_property_detail(property_url)
            page_data_list.append(data)
            print(page_data_list)

    return page_data_list