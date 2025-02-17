import requests
from requests.exceptions import RequestException
import config  

class APIClient:
    def __init__(self, base_url, api_key=None, rapidapi_key=None, rapidapi_host=None):
        self.base_url = base_url
        self.api_key = api_key
        self.rapidapi_key = rapidapi_key
        self.rapidapi_host = rapidapi_host
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        if self.rapidapi_key and self.rapidapi_host:
            self.headers["x-rapidapi-key"] = self.rapidapi_key
            self.headers["x-rapidapi-host"] = self.rapidapi_host

    def _make_request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"Error al hacer la solicitud: {e}")
            return None

    def get_property_details(self, zpid):
        """Obtiene los detalles de una propiedad por su ZPID."""
        endpoint = "properties/details"
        querystring = {"zpid": zpid}
        return self._make_request("GET", endpoint, params=querystring)

    def get_weather(self, city):
        """Obtiene el clima actual de una ciudad usando OpenWeatherMap."""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": config.OPENWEATHERMAP_API_KEY,  
            "units": "metric"  
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"Error al obtener el clima: {e}")
            return None

    def get_nearby_places(self, latitude, longitude, radius=5000, place_type="school"):
        """Obtiene lugares cercanos usando Google Maps API."""
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"  
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "type": place_type,
            "key": config.GOOGLE_PLACES_API_KEY  
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"Error al obtener lugares cercanos: {e}")
            return None

