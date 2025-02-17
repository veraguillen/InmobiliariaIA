from fastapi import FastAPI
from pydantic import BaseModel
from colorama import init

# Inicializar colorama
init()

# Inicializar FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class ZPIDRequest(BaseModel):
    zpid: str

@app.get("/property_details/{zpid}")
def get_property_details(zpid: str):
    from api_client import APIClient
    import config
    from utils import print_color, extract_address_from_description

    def format_number(value):
        if isinstance(value, (int, float)) and value >= 0:
            return value
        elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
            return float(value) if '.' in value else int(value)
        return 'No se encontró dato'

    def get_formatted_chip_value(chip_data, fact_type):
        for fact in chip_data.get('quickFacts', []):
            if fact.get('elementType') == fact_type:
                return fact.get('value', {}).get('fullValue', 'No se encontró dato')
        return 'No se encontró dato'

    def format_description(description):
        if not description:
            return 'No se encontró dato'
        
        words = description.split()
        formatted_description = ''
        line = ''
        for i, word in enumerate(words, 1):
            line += word + ' '
            if i % 10 == 0:
                formatted_description += line.strip() + '\n'
                line = ''
        formatted_description += line.strip()  
        return formatted_description

    def print_property_details(data, zpid, client):
        if not data:
            return {"message": "No se encontraron datos de la propiedad."}

        details = {
            "Dirección": data.get('address', {}).get('streetAddress', 'No se encontró dato'),
            "Ciudad": data.get('address', {}).get('city', 'No se encontró dato'),
            "Estado": data.get('address', {}).get('state', 'No se encontró dato'),
            "Código Postal": data.get('address', {}).get('zipcode', 'No se encontró dato'),
            "Precio": format_number(data.get('price')),
            "Zestimate": format_number(data.get('zestimate')),
            "Descripción": format_description(data.get('description', 'No se encontró dato')),
            "Baños": format_number(data.get('bathrooms')),
            "Habitaciones": format_number(data.get('bedrooms')),
            "Área": format_number(data.get('livingAreaValue')),
            "Tipo de propiedad": data.get('resoFacts', {}).get('homeType', 'No se encontró dato'),
            "Año de construcción": data.get('resoFacts', {}).get('yearBuilt', 'No se encontró dato'),
            "Tamaño del lote": data.get('resoFacts', {}).get('lotSize', 'No se encontró dato'),
            "Calefacción": ', '.join(data.get('resoFacts', {}).get('heating', ['No se encontró dato'])),
            "Refrigeración": ', '.join(data.get('resoFacts', {}).get('cooling', ['No se encontró dato'])),
            "Pisos": ', '.join(data.get('resoFacts', {}).get('flooring', ['No se encontró dato'])),
        }

        # Obtener datos del clima
        city = details["Ciudad"]
        if city:
            weather_data = client.get_weather(city)
            if weather_data:
                details["Clima"] = {
                    "Descripción": weather_data.get('weather', [{}])[0].get('description'),
                    "Temperatura": weather_data.get('main', {}).get('temp')
                }
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude and longitude:
            details["Coordenadas"] = f"Latitud={latitude}, Longitud={longitude}"

            # Obtener lugares cercanos
            details["Lugares cercanos"] = {
                "Escuelas": [school.get('name') for school in client.get_nearby_places(latitude, longitude, place_type="school").get('results', [])[:3]],
                "Hospitales": [hospital.get('name') for hospital in client.get_nearby_places(latitude, longitude, place_type="hospital").get('results', [])[:3]],
                "Tiendas": [store.get('name') for store in client.get_nearby_places(latitude, longitude, place_type="store").get('results', [])[:3]],
            }
        else:
            details["Coordenadas"] = "No se encontraron coordenadas en los detalles de la propiedad."

        return details

    client = APIClient(
        base_url=config.API_BASE_URL,
        rapidapi_key=config.RAPIDAPI_KEY,
        rapidapi_host=config.RAPIDAPI_HOST
    )

    property_details = client.get_property_details(zpid)
    if property_details and property_details.get('status'):
        data = property_details.get('data', {})
        return print_property_details(data, zpid, client)
    else:
        return {"message": "No se pudieron obtener los detalles de la propiedad"}

# Ejecutar la aplicación con uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
