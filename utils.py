from colorama import Fore, Style
import re

def print_color(text, color="white", bold=False):
    """
    Imprime texto en color en la consola.
    
    :param text: Texto a imprimir.
    :param color: Nombre del color (ej: "green", "cyan", "yellow").
    :param bold: Si el texto debe estar en negrita.
    """
    color_code = COLORS.get(color, Fore.WHITE)  
    if bold:
        text = Style.BRIGHT + text + Style.RESET_ALL
    print(color_code + text + Style.RESET_ALL)

def extract_address_from_description(description):
    #Extrae la dirección, ciudad, estado y código postal de la descripción.
    
    if not description:
        return None, None, None, None
    
    # Expresión regular para extraer la dirección
    pattern = r"(\d+\s[\w\s]+),\s([\w\s]+),\s([A-Z]{2})\s(\d{5})"
    match = re.search(pattern, description)
    
    if match:
        street_address = match.group(1).strip()
        city = match.group(2).strip()
        state = match.group(3).strip()
        zipcode = match.group(4).strip()
        return street_address, city, state, zipcode
    return None, None, None, None

# Diccionario de colores
COLORS = {
    "green": Fore.GREEN,
    "cyan": Fore.CYAN,
    "yellow": Fore.YELLOW,
    "white": Fore.WHITE,
    "magenta": Fore.MAGENTA,
    "blue": Fore.BLUE,
    "red": Fore.RED,
}
