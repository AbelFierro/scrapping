# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tasador import geocode_direccion, categorizar_antiguedad, obtener_comparables
from fastapi import HTTPException
import numpy as np

app = FastAPI()

# Permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputDatos(BaseModel):
    barrio: str
    direccion: str
    ambientes: int
    banos: int
    antiguedad: int
    cercania: float
    m2: float

@app.post("/tasar")

def tasar_propiedad(data: InputDatos):
    try:
        print("📩 Recibido:", data)
        data.direccion = data.direccion.upper()
        print(data.direccion)
        lat, lon = geocode_direccion(data.direccion)
        print(lat)
        print(lon)
        if lat is None or lon is None:
            return {"error": "No se pudo geolocalizar la dirección."}

        rango_ant = categorizar_antiguedad(data.antiguedad)
        comparables = obtener_comparables(lat, lon, data.ambientes, data.banos, rango_ant, data.cercania)

        if comparables.empty:
            print("❌ No se encontraron comparables.")
            raise HTTPException(status_code=404, detail="No se encontraron propiedades comparables.")
        
        import numpy as np

        comparables = comparables.replace([np.inf, -np.inf], np.nan)
        #print(comparables['precio_m2']) 
        valor_estimado = comparables['precio_m2'].mean()
        valor_total = valor_estimado * data.m2
        #print(valor_estimado)

        import numpy as np
        comparables = comparables.replace({np.nan: None})
        comparables = comparables.replace([np.inf, -np.inf], np.nan).dropna()
        #print(comparables)
        

        comparables_dict = comparables[[
            'Direccion', 'Ambientes', 'Baños', 'Publicada_en', 'Cubierta',
            'Antigüedad', 'Precio', 'distancia_km','lat','lon'
        ]].to_dict(orient="records")
        
        """
        import math

        def clean_dict(d):
            for key, value in d.items():
                if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    d[key] = None
                elif isinstance(value, dict):
                    clean_dict(value)
            return d

        comparables_dict = clean_dict(comparables_dict)

        """
        #print(comparables_dict)
        return {
            "valor_m2": round(valor_estimado, 2),
            "valor_total": round(valor_total, 2),
            "comparables": comparables_dict,
            "geo": [float(lat), float(lon)]
        }
    except Exception as e:
        import traceback
        print("💥 ERROR:", str(e))
        traceback.print_exc()
        raise e 