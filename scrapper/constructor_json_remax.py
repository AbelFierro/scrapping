import os
import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm

# 📁 Carpeta con todos los archivos HTML
HTML_DIR = "/home/gugui/Documentos/Austral/Austral/Web Mining/Trabajo Final/remax_large/caba/palermo"
OUTPUT_JSON = "/home/gugui/Documentos/Austral/Austral/Web Mining/Trabajo Final/remax_large/full-data-limpia-remax.json"

def extract_with_regex(text, label):
    patterns = {
        "Total": r"(\d+(?:[.,]\d+)?)\s*m²\s*totales",
        "Cubierta": r"(\d+(?:[.,]\d+)?)\s*m²\s*cubiertos",
        "Ambientes": r"(\d+)\s*ambientes?",
        "Baños": r"(\d+)\s*bañ[óo]s?",
        "Toilet": r"(\d+)\s*toilet",
        "Antigüedad": r"(\d+)\s*a[ñn]os\s*antigüedad"
    }
    match = re.search(patterns[label], text, re.IGNORECASE)
    if match:
        value = match.group(1).replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return 0
    return 0


def parse_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    data = {
        "titulo": soup.title.string.strip() if soup.title else "0",
        "operacion": soup.find("meta", {"name": "description"}).get("content", "0") if soup.find("meta", {"name": "description"}) else "0",
        "direccion": "0",
        "Precio": "0",
        "Ambientes": "0",
        "Baños": "0",
        "Total": "0",
        "Cubierta": "0",
        "Descubierta": "0",
        "Balcón": "0",
        "Antigüedad": "0",
        "Disposición": "0",
        "https": soup.find("link", rel="canonical").get("href", "0") if soup.find("link", rel="canonical") else "0"
    }

    # Dirección (si hay keywords)
    keywords = soup.find("meta", {"name": "keywords"})
    if keywords:
        partes = keywords.get("content", "").split(",")
        if len(partes) > 1:
            data["direccion"] = partes[1].strip()

    # Precio
    match_precio = re.search(r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?\s*USD)", text)
    if match_precio:
        data["Precio"] = match_precio.group(1).replace(" ", "")
    elif "solicitar precio" in text.lower():
        data["Precio"] = "Solicitar precio"

    # Extraer con regex
    total = extract_with_regex(text, "Total")
    cubierta = extract_with_regex(text, "Cubierta")
    descubierta = max(0, total - cubierta)
    ambientes = extract_with_regex(text, "Ambientes")
    banos = extract_with_regex(text, "Baños")
    toilets = extract_with_regex(text, "Toilet")
    antiguedad = extract_with_regex(text, "Antigüedad")
    
    data["Total"] = f"{total:.2f} m²" if total else "0"
    data["Cubierta"] = f"{cubierta:.2f} m²" if cubierta else "0"
    data["Descubierta"] = f"{max(0, total - cubierta):.2f} m²" if total and cubierta else "0"
    data["Ambientes"] = str(ambientes)
    data["Baños"] = str(banos + toilets)
    data["Antigüedad"] = f"{antiguedad} años" if antiguedad else "0"

    # Disposición
    if "disposición: frente" in text.lower():
        data["Disposición"] = "Frente"
    elif "disposición: contrafrente" in text.lower():
        data["Disposición"] = "Contrafrente"

    return data

# 📂 Archivos HTML
html_files = [f for f in os.listdir(HTML_DIR) if f.endswith(".html")]
html_files.sort()

print(f"🔍 Procesando {len(html_files)} archivos...")
resultados = []

for file in tqdm(html_files):
    try:
        full_path = os.path.join(HTML_DIR, file)
        resultados.append(parse_html(full_path))
    except Exception as e:
        print(f"❌ Error en {file}: {e}")

# 💾 Guardar JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"\n✅ ¡Hecho! JSON generado en:\n{OUTPUT_JSON}")
