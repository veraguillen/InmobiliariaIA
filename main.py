from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class ZPIDRequest(BaseModel):
    zpid: str

@app.get("/property_details/{zpid}")
def get_property_details(zpid: str):
    from colorama import init
    init()  

    from api_client import APIClient
    import config
    from utils import print_color, extract_address_from_description

    def format_number(value):
        """
        Formatea un valor numérico. Si no es válido, devuelve 'No se encontró dato'.
        """
        if isinstance(value, (int, float)) and value >= 0:
            return value
        elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
            return float(value) if '.' in value else int(value)
        return 'No se encontró dato'

    def get_formatted_chip_value(chip_data, fact_type):
        """
        Obtiene el valor de formattedChip para un tipo de característica específica.
        """
        for fact in chip_data.get('quickFacts', []):
            if fact.get('elementType') == fact_type:
                return fact.get('value', {}).get('fullValue', 'No se encontró dato')
        return 'No se encontró dato'

    def format_description(description):
        """
        Formatea la descripción para que cada línea tenga un máximo de 10 palabras.
        """
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
        """
        Imprime los detalles de la propiedad de manera formateada.
        """
        if not data:
            print_color("No se encontraron datos de la propiedad.", color="red", bold=True)
            return

        print_color("=== Detalles de la Propiedad ===", color="green", bold=True)
        
        # Dirección
        address = data.get('address', {})
        street_address = address.get('streetAddress')
        city = address.get('city')
        state = address.get('state')
        zipcode = address.get('zipcode')
        
        # Si la dirección no está disponible en 'address', extraé de la descripción
        if not all([street_address, city, state, zipcode]):
            description = data.get('description', '')
            street_address, city, state, zipcode = extract_address_from_description(description)
        
        print_color(f"Dirección: {street_address or 'No se encontró dato'}", color="cyan")
        print_color(f"Ciudad: {city or 'No se encontró dato'}", color="cyan")
        print_color(f"Estado: {state or 'No se encontró dato'}", color="cyan")
        print_color(f"Código Postal: {zipcode or 'No se encontró dato'}", color="cyan")
        
        # Manejo de excepciones para código ZIP inválido
        if zipcode == 'No se encontró dato':
            print_color("Advertencia: El código postal no es válido. Los detalles de la propiedad pueden estar incompletos.", color="red")
        
        # Precio y Zestimate
        price = format_number(data.get('price'))
        zestimate = format_number(data.get('zestimate'))
        print_color(f"Precio: ${price:,}", color="yellow", bold=True)
        print_color(f"Zestimate: ${zestimate:,}", color="yellow", bold=True)
        
        # Características principales
        description = format_description(data.get('description', 'No se encontró dato'))
        print_color(f"Descripción:\n{description}", color="white")
        
        # Obtener valores de formattedChip
        formatted_chip = data.get('formattedChip', {})
        
        # Validar y formatear baños y habitaciones
        bathrooms = format_number(data.get('bathrooms'))
        if bathrooms == 'No se encontró dato':
            bathrooms = get_formatted_chip_value(formatted_chip, 'baths')
        print_color(f"Baños: {bathrooms}", color="magenta")
        
        bedrooms = format_number(data.get('bedrooms'))
        if bedrooms == 'No se encontró dato':
            bedrooms = get_formatted_chip_value(formatted_chip, 'beds')
        print_color(f"Habitaciones: {bedrooms}", color="magenta")
        
        # Área
        living_area = format_number(data.get('livingAreaValue'))
        if living_area == 'No se encontró dato':
            living_area = get_formatted_chip_value(formatted_chip, 'livingArea')
        print_color(f"Área: {living_area} sqft", color="magenta")
        
        # Detalles adicionales 
        reso_facts = data.get('resoFacts', {})
        print_color(f"Tipo de propiedad: {reso_facts.get('homeType', 'No se encontró dato')}", color="magenta")
        print_color(f"Año de construcción: {reso_facts.get('yearBuilt', 'No se encontró dato')}", color="magenta")
        print_color(f"Tamaño del lote: {reso_facts.get('lotSize', 'No se encontró dato')}", color="magenta")
        print_color(f"Calefacción: {', '.join(reso_facts.get('heating', ['No se encontró dato']))}", color="magenta")
        print_color(f"Refrigeración: {', '.join(reso_facts.get('cooling', ['No se encontró dato']))}", color="magenta")
        print_color(f"Pisos: {', '.join(reso_facts.get('flooring', ['No se encontró dato']))}", color="magenta")
        
        # Enlace
        #print_color(f"Enlace: https://www.zillow.com/homedetails/{zpid}_zpid/", color="blue")
        
        # Datos del clima
        if city:
            weather_data = client.get_weather(city)
            if weather_data:
                temperature = weather_data.get('main', {}).get('temp')
                weather_description = weather_data.get('weather', [{}])[0].get('description')
                print_color(f"Clima en {city}: {weather_description}, Temperatura: {temperature}°C", color="cyan", bold=True)
        
        #Latitud y Longitud 
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude and longitude:
            print_color(f"Coordenadas: Latitud={latitude}, Longitud={longitude}", color="cyan")
            
            #Lugares cercanos 
            print_color("=== Lugares Cercanos ===", color="green", bold=True)
            
            # Escuelas
            schools = client.get_nearby_places(latitude, longitude, place_type="school")
            if schools and schools.get('results'):
                print_color("Escuelas cercanas:", color="magenta")
                for school in schools.get('results', [])[:3]:  # Muestra las 3 primeras
                    print_color(f"- {school.get('name')}", color="magenta")
            
            # Hospitales
            hospitals = client.get_nearby_places(latitude, longitude, place_type="hospital")
            if hospitals and hospitals.get('results'):
                print_color("Hospitales cercanos:", color="magenta")
                for hospital in hospitals.get('results', [])[:3]:  # Muestra las 3 primeras
                    print_color(f"- {hospital.get('name')}", color="magenta")
            
            # Tiendas
            stores = client.get_nearby_places(latitude, longitude, place_type="store")
            if stores and stores.get('results'):
                print_color("Tiendas cercanas:", color="magenta")
                for store in stores.get('results', [])[:3]:  # Muestra las 3 primeras
                    print_color(f"- {store.get('name')}", color="magenta")
        else:
            print_color("No se encontraron coordenadas en los detalles de la propiedad.", color="red")

    # Inicializar el cliente
    client = APIClient(
        base_url=config.API_BASE_URL,
        rapidapi_key=config.RAPIDAPI_KEY,
        rapidapi_host=config.RAPIDAPI_HOST
    )

    # Obtener detalles de la propiedad
    property_details = client.get_property_details(zpid)
    if property_details and property_details.get('status'):
        data = property_details.get('data', {})
        print_property_details(data, zpid, client)
    else:
        return {"message": "No se pudieron obtener los detalles de la propiedad"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
