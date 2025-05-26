import os
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime
import hashlib
import re

FEATURES_LIST = [
    "Superficie total", "Ambientes", "Baños", "Dormitorios", "Sup. Cubierta",
    "Antigüedad", "Cocheras"
]

NUMERIC_FEATURES = {
    "Superficie total", "Ambientes", "Baños", "Dormitorios", "Sup. Cubierta",
    "Antigüedad", "Cocheras"
}

def clean_numeric(value):
    if not value:
        return 0
    match = re.search(r'\d+(?:[.,]\d+)?', value)
    return float(match.group(0).replace(",", ".")) if match else 0

def extract_property_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    url = soup.find('meta', property='og:url')
    url = url['content'] if url else None
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest() if url else None

    scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    features = {key: 0 for key in FEATURES_LIST}

    # Extraer características del bloque de detalles
    details_section = soup.find('section', class_='details')
    if details_section:
        for detail in details_section.find_all('div', class_='detail'):
            icon = detail.find('img', class_='detail__icon')
            text = detail.find('p', class_='detail__text')
            if icon and text:
                label = icon['alt'].strip()
                if label in FEATURES_LIST:
                    value = text.get_text(strip=True)
                    features[label] = clean_numeric(value)

    # Extraer dirección desde el breadcrumb
    address = None
    breadcrumb = soup.find('section', class_='breadcrumb breadcrumb--desktop')
    if breadcrumb:
        items = breadcrumb.find_all('li')
        if items:
            last = items[-1]
            span = last.find('span')
            if span:
                address = span.get_text(strip=True)

    return {
        "titulo": soup.title.string.strip() if soup.title else "0",
        "operacion": soup.find("meta", {"name": "description"}).get("content", "0") if soup.find("meta", {"name": "description"}) else "0",
        "direccion": address if address else "0",
        "Precio": soup.find('div', class_='prices__price').get_text(strip=True).replace("USD", "").strip() + "USD" if soup.find('div', class_='prices__price') else "0",
        "Ambientes": str(int(features["Ambientes"])) if features["Ambientes"] else "0",
        "Baños": str(int(features["Baños"])) if features["Baños"] else "0",
        "Total": f'{features["Superficie total"]:.2f} m²' if features["Superficie total"] else "0",
        "Cubierta": f'{features["Sup. Cubierta"]:.2f} m²' if features["Sup. Cubierta"] else "0",
        "Descubierta": f'{max(0, features["Superficie total"] - features["Sup. Cubierta"]):.2f} m²' if features["Superficie total"] and features["Sup. Cubierta"] else "0",
        "Balcón": "0",
        "Antigüedad": f'{int(features["Antigüedad"])} años' if features["Antigüedad"] else "0",
        "Disposición": "0",  # Podés agregar lógica adicional si la encontrás en el HTML
        "https": url if url else "0"
    }

def process_directory(directory_path):
    results = []
    html_files = [f for f in os.listdir(directory_path) if f.endswith('.html')]
    html_files.sort()

    print(f"🔍 Procesando {len(html_files)} archivos...")

    for filename in tqdm(html_files, desc="Procesando archivos"):
        file_path = os.path.join(directory_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                property_data = extract_property_data(html_content)
                results.append(property_data)
        except Exception as e:
            print(f"❌ Error en {filename}: {e}")
            continue

    return results

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ ¡Datos guardados correctamente en:\n{output_file}")

# Main
if __name__ == "__main__":
    HTML_DIR = "/home/gugui/Documentos/Austral/Austral/Web Mining/Trabajo Final/mudafy_large/caba/palermo"
    OUTPUT_JSON = "/home/gugui/Documentos/Austral/Austral/Web Mining/Trabajo Final/mudafy_large/full-data-limpia-mudafy.json"

    data = process_directory(HTML_DIR)
    save_to_json(data, OUTPUT_JSON)