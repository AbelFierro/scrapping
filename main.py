from constants import *
from scrappagecaba import scrap_page
#from scrappageargen import scrap_page_argen
#from scrappagezona import scrap_page_zona
from crawler import SeleniumGetHTML
from helpers import listToJSON
import os
import json
import unicodedata
import re

# === Config inicial ===


# 1) Define tu mapeo raw → estándar
KEY_MAPPING = {
    "Dirección":        "Direccion",
    "Cant. Ambientes":  "Ambientes",
    "Cant. Dormitorios":"Dormitorio",
    "Cant. Baños":      "Baños",
    "Estado":           "Estado",
    "Antiguedad":       "Antiguedad",
    "Disposición":      "Disposicion",
    "Orientación":      "Orientacion",
    "Tipo de Piso":     "Tipo_piso",
    "Expensas":         "Expensas",
    "Tipo de Unidad":   "Tipo_unidad",
    "Tipo de operación":"Tipo_operacion",
    "Precio":           "Precio",
    "Sup. Cubierta":    "Sup_cubierta",
    "Sup. Total":       "Sup_total",
    "Cant. Pisos":      "Cantidad_pisos",
    "Deptos. por Piso": "Deptos_por_piso",
    "Estado Edificio":  "Estado_edificio"
}

def limpiar_data_argen(data):
    # paso A: parsear raw "clave: valor"
    raw = {}
    for entry in data:
        if ':' in entry:
            key, val = entry.split(':', 1)
            key = key.strip()
            val = val.strip()
            if key:
                raw[key] = val

    # paso B: renombrar según el mapeo
    renamed = {}
    for raw_key, val in raw.items():
        new_key = KEY_MAPPING.get(raw_key, raw_key)  # si no está en el mapeo, deja la clave original
        renamed[new_key] = val

    # si quieres devolverlo dentro de una lista como antes:
    return [renamed]

def normalizar_barrio(barrio):
    # Convertir a minúsculas si querés URLs homogéneas (opcional)
    # barrio = barrio.lower()

    # Quitar tildes y convertir ñ → n
    barrio = unicodedata.normalize("NFKD", barrio).encode("ascii", "ignore").decode("ascii")

    # Reemplazar espacios por guión bajo
    barrio = barrio.replace(" ", "_")

    # Eliminar caracteres que no sean alfanuméricos o guiones bajos
    barrio = re.sub(r"[^a-zA-Z0-9_]", "", barrio)
    
    barrio=barrio.lower()

    return barrio



def limpiar_data_caba(data):
    result = {
        "estado": None, "piso": None, "titulo": None, "tipo": None,
        "direccion": None, "ubicacion": None, "ambientes": None,
        "dormitorio": None, "baño": None, "cochera": "0",
        "m2_totales": None, "m2_cubiertos": None,
        "fecha_publicacion": None, "precio": None
    }
    #print(data)
    
    property_dict = {}

    try:
        
    # Paso 2: extraer título, operación, dirección
        titulo = data[0]
        operacion = data[1]
        direccion = data[2]

    # Paso 3: buscar claves que tengan formato "clave: valor"
        property_dict = {
            "Titulo": titulo,
            "Operacion": operacion,
            "Direccion": direccion
        }

        for i in range(3, len(data)):
            if ':' in data[i]:
                partes = data[i].split(':', 1)
                clave = partes[0].strip()
                valor = partes[1].strip()
                if clave and valor:
                    property_dict[clave] = valor

        

    except Exception as e:
        result["error"] = str(e)
        result["raw"] = data
    #print(property_dict)
    return property_dict

def main():
    global archivo_indice 
    global barrios_procesados
    barrios_procesados = set()
    archivo_indice = "barrios_procesados.json"
    # Cargar barrios procesados si existen
    if os.path.exists(archivo_indice):
        with open(archivo_indice, "r", encoding="utf-8") as f:
            barrios_procesados = set(json.load(f))
    data_list = []
    result_dict = {key: [] for key in COMPANY_FIELDS}

    option = input("Elige una opción:\n1. Scrapear Cabaprop\n2. Scrapear Zonaprop\n3. Scrapear Argenprop\n> ")

    try:
        option = int(option)
    except ValueError:
        print("Error: Solo escribe 1 o 2")
        return
    
    


    if option == 1:
        continuar = input("¿Querés continuar desde donde se cortó? (s/n): ").lower() == "s"
        if not continuar:
            barrios_procesados = set()
            if os.path.exists(archivo_indice):
                os.remove(archivo_indice)
                
        for barrio in BARRIOS:
            data_list = []
            if barrio in barrios_procesados:
                print(f"⏭ Barrio ya procesado: {barrio}")
                continue
            index = 1
            barrio_encoded = barrio.replace(" ", "%20")
            barrio_encoded = normalizar_barrio(barrio)
            print(barrio_encoded)
            while (True):
                try:
                    #comprar-palermo?pagina=1
                    url = BASE_URL + f"{barrio_encoded}?pagina={index}"
                    print(f"Scrapeando: {url}------------------------------------->>>>>>")
                    #print("barrios_procesados:", barrios_procesados)
                    
                    html_content = SeleniumGetHTML(url,headless=True)
                    if "No existen inmobiliarias con esas características" in html_content:
                        print("Llegaste al final de los resultados, continuando con el siguiente barrio")
                        break
                    #print(html_content)
                    #print("barrios_procesados:", barrios_procesados)
                    results = scrap_page(html_content)
                    
                    #print(results)
                    if not results:
                        print(f"No se encontraron datos en la página {index} de {barrio}")
                        break
                    
                    data_list.extend(results)
                    print(f"Cantidad de propiedades scrapeadas para {barrio}: {len(data_list)}")
                    #clddata_list 
                    index += 1
                
                except Exception as e:
                    print(f"Error al scrapear {url}: {e}")
                    break  # Continuar con el siguiente barrio si hay un problema

            # Guardar datos completos
                #print("entra aqui y aqui")
            try:
                # Limpiar todos los elementos}
                    #print("entra aqui****************************")
                    #print(barrio)
                nombre_archivo = f"full-data_zonaprop_{barrio.replace(' ', '_')}.json"
                    #print(nombre_archivo)
                
                data_limpia = [limpiar_data_caba(propiedad) for propiedad in data_list]
                
                
                    # Guardar en JSON
                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    json.dump(data_limpia, f, ensure_ascii=False, indent=2)
                    
                    # Agregar a barrios procesados y actualizar índice
                barrios_procesados.add(barrio)
                with open(archivo_indice, "w", encoding="utf-8") as f:
                    json.dump(list(barrios_procesados), f, ensure_ascii=False, indent=2)    
            
        
            except Exception as e:
                print(f"Error al guardar archivos de datos: {e}")

        # Convertir a JSON y exportar a Excel
        #try:
         #   for lst in data_list:
          #      listToJSON(lst, result_dict)
           # toExcel(result_dict)
        #except Exception as e:
         #   print(f"Error al generar JSON o Excel: {e}")

    elif option == 2:
            index = 1
            #barrio_encoded = barrio.replace(" ", "%20")
            barrio="palermo"
            while (index <= 476):
                try:
                    #comprar-palermo?pagina=1
                    url = f"https://www.zonaprop.com.ar/departamentos-venta-pagina-{index}-q-palermo.html"
                    print(f"Scrapeando: {url}")
                    
                    html_content = SeleniumGetHTML(url)
                    if "No existen inmobiliarias con esas características" in html_content:
                        print("Llegaste al final de los resultados, continuando con el siguiente barrio")
                        break
                    
                    results = scrap_page_zona(html_content)
                    print(results)
                    if not results:
                        print(f"No se encontraron datos en la página {index} de {barrio}")
                        break
                    print (data_list)
                    print(f"Cantidad de propiedades scrapeadas para {barrio}: {len(data_list)}")
                    
                    data_list.extend(results)
                    #clddata_list 
                    print("sale del scrapper------------------>>>>>>>>>>>>>>>>>>>>>>>")
                    print(data_list)
                    index += 1
                
                except Exception as e:
                    print(f"Error al scrapear {url}: {e}")
                    break  # Continuar con el siguiente barrio si hay un problema

            # Guardar datos completos
            #data_list
            try:
            # Limpiar todos los elementos
                data_limpia = [limpiar_data(propiedad) for propiedad in data_list]

            # Guardar en JSON
                with open("full-data_zonaprop.json", "w", encoding="utf-8") as f:
                    json.dump(data_limpia, f, ensure_ascii=False, indent=2)
            
        
            except Exception as e:
                print(f"Error al guardar archivos de datos: {e}")

            # Convertir a JSON y exportar a Excel
            try:
                for lst in data_list:
                    listToJSON(lst, result_dict)
                toExcel(result_dict)
            except Exception as e:
                print(f"Error al generar JSON o Excel: {e}")
    elif option == 3:
            index = 1
            #barrio_encoded = barrio.replace(" ", "%20")
            barrio="palermo"
            while (index <= 476):
                try:
                    #comprar-palermo?pagina=1
                    url = f"https://www.argenprop.com/departamentos/venta/palermo?pagina-{index}"
                    print(f"Scrapeando: {url}")
                    
                    html_content = SeleniumGetHTML(url)
                    if "No existen inmobiliarias con esas características" in html_content:
                        print("Llegaste al final de los resultados, continuando con el siguiente barrio")
                        break
                    
                    results = scrap_page_argen(html_content)
                    print(results)
                    if not results:
                        print(f"No se encontraron datos en la página {index} de {barrio}")
                        break
                    print (data_list)
                    print(f"Cantidad de propiedades scrapeadas para {barrio}: {len(data_list)}")
                    
                    data_list.extend(results)
                    #clddata_list 
                    print("sale del scrapper------------------>>>>>>>>>>>>>>>>>>>>>>>")
                    print(data_list)
                    index += 1
                
                except Exception as e:
                    print(f"Error al scrapear {url}: {e}")
                    break  # Continuar con el siguiente barrio si hay un problema

            # Guardar datos completos
            #data_list
            try:
            # Limpiar todos los elementos
                data_limpia = [limpiar_data_argen(propiedad) for propiedad in data_list]

            # Guardar en JSON
                with open("full-data_argenprop.json", "w", encoding="utf-8") as f:
                    json.dump(data_limpia, f, ensure_ascii=False, indent=2)
            
        
            except Exception as e:
                print(f"Error al guardar archivos de datos: {e}")

            # Convertir a JSON y exportar a Excel
            try:
                for lst in data_list:
                    listToJSON(lst, result_dict)
                toExcel(result_dict)
            except Exception as e:
                print(f"Error al generar JSON o Excel: {e}")
    else:
        print("Opción inválida")

# Ejecutar el script
if __name__ == "__main__":
    main()
