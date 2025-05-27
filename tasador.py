# tasador.py
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

def geocode_direccion(direccion):
    geolocator = Nominatim(user_agent="tasador-app")
    location = geolocator.geocode(direccion + ", CABA, Argentina")
    if location:
        return (location.latitude, location.longitude)
    else:
        return None, None
def manhattan_distance_km(lat1, lon1, lat2, lon2):
    # Aproximadamente 111km por grado
    return abs(lat1 - lat2) * 111 + abs(lon1 - lon2) * 96

def categorizar_antiguedad(antiguedad):
    try:
        antiguedad = int(antiguedad)
    except:
        return None

    if antiguedad == 0:
        return 0
    elif antiguedad <= 5:
        return 1
    elif antiguedad <= 10:
        return 2
    elif antiguedad <= 20:
        return 3
    elif antiguedad <= 40:
        return 4
    else:
        return 5

def obtener_comparables(lat, lon, ambientes, banos, rango_ant, max_km):
    

    cabaprop = pd.read_json("datos_geolocalizados_cabaprop.json", orient="records")
    remax = pd.read_json("datos_geolocalizados_remax.json", orient="records")
    mudafy = pd.read_json("datos_geolocalizados_mudafy.json", orient="records")
    argen = pd.read_json("datos_geolocalizados_argenprop.json", orient="records")
    zona = pd.read_json("datos_geolocalizados_zonaprop.json", orient="records")
    print(zona)
    mudafy['Publicada_en']="Mudafy"
    df= pd.concat([cabaprop, remax, mudafy,argen,zona], ignore_index=True)
    df = df[['Direccion', 'Precio', 'Ambientes', 'Baños', 'Total', 'Cubierta', 'Antigüedad', 'Publicada_en', 'Categoria_antigüedad', 'lat', 'lon']]

    comparables = df[
        (df['Ambientes'] == ambientes) &
        (df['Baños'] == banos) &
        (df['Categoria_antigüedad'] == rango_ant) &
        (df['lat'].notna()) & (df['lon'].notna())
    ].copy()

    comparables["distancia_km"] = comparables.apply(
        lambda row: manhattan_distance_km(lat, lon, row["lat"], row["lon"]),
        axis=1
    )

    comparables = comparables[comparables["distancia_km"] <= max_km]
    comparables['precio_m2'] = comparables['Precio'] / comparables['Cubierta']
    print()
    return comparables
