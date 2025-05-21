from urllib.parse import urlparse, urlunparse
from threading import Lock
import concurrent.futures
from PIL import Image
from tqdm import tqdm
import itertools
import requests
import os
import io
import csv
import json

IMGS = "_1. Imagenes/"
os.makedirs(IMGS, exist_ok=True)

# --- Configuración dinámica de APIs ---
def cargar_configuracion_deepinfra():
    config_path = os.path.join("config", "ai_config.json")
    if not os.path.exists(config_path):
        print("No existe archivo de configuración.")
        return "", "stabilityai/sd3.5-medium"  # API key vacía y modelo por defecto
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        print(f"Leyendo configuración para DeepInfra...")
        
        # Buscar la API key de DeepInfra
        api_key = config.get("image_api_key", "")
        
        # Buscar el modelo configurado, o usar uno por defecto
        model = config.get("image_model", "")
        if not model:
            model = "black-forest-labs/FLUX-1-schnell"  # Modelo predeterminado si no hay ninguno configurado
            print(f"No hay modelo configurado. Usando modelo por defecto: {model}")
        else:
            print(f"Usando modelo configurado: {model}")
        
        return api_key, model
        
    except Exception as e:
        print(f"Error al cargar configuración para DeepInfra: {e}")
        return "", "black-forest-labs/FLUX-1-schnell"  # Valores por defecto en caso de error

# Cargar API key y modelo de DeepInfra
deepinfra_api_key, deepinfra_model = cargar_configuracion_deepinfra()

# URL base de la API de DeepInfra
deepinfra_api_url = "https://api.deepinfra.com/v1/openai/images/generations"

# Lock para sincronizar peticiones
api_lock = Lock()
# --- Fin configuración dinámica de APIs ---

def crear_imagen(imagen, prompt):
    ruta_imagen = os.path.join(IMGS, imagen)
    if os.path.exists(ruta_imagen):
        print(f"Imagen {imagen} ya existe, omitiendo generación")
        return True
    
    # Verificar si tenemos una API key
    if not deepinfra_api_key:
        print(f"Error: No se ha configurado una API key para DeepInfra")
        return False
    
    # Configurar los headers con la API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {deepinfra_api_key}"
    }
    
    # Configurar la petición para DeepInfra
    data = {
        "prompt": prompt,
        "model": deepinfra_model,  # Usar el modelo configurado 
        "size": "1024x1024",       # Tamaño estándar
        "n": 1                     # Generar 1 imagen
    }
    
    # Añadir negative prompt si es necesario según el modelo
    if "sd3" in deepinfra_model.lower() or "stable-diffusion" in deepinfra_model.lower():
        data["negative_prompt"] = "worst quality, low quality, deformed, distorted, disfigured, bad anatomy"
    
    try:
        print(f"Generando imagen '{imagen}' con DeepInfra usando modelo {deepinfra_model}")
        with api_lock:
            # Hacer la petición a DeepInfra
            response = requests.post(deepinfra_api_url, headers=headers, json=data, timeout=60)
            
            # Verificar si la petición fue exitosa
            if response.status_code != 200:
                error_msg = f"Error en API DeepInfra: {response.status_code} - {response.text}"
                print(error_msg)
                return False
            
            # Procesar la respuesta
            response_json = response.json()
            
            # Imprimir la estructura de la respuesta para diagnóstico
            print(f"Estructura de respuesta DeepInfra: {json.dumps(response_json, indent=2)[0:200]}...")
            
            # Verificar formato de respuesta de la API de OpenAI
            if "data" in response_json and len(response_json["data"]) > 0:
                first_image = response_json["data"][0]
                
                # Verificar si existe b64_json (respuesta en base64) o url
                if "b64_json" in first_image:
                    print("Imagen recibida en formato base64")
                    import base64
                    image_data = first_image["b64_json"]
                    image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                    
                elif "url" in first_image:
                    print("Imagen recibida como URL")
                    image_url = first_image["url"]
                    response_image = requests.get(image_url, timeout=30)
                    
                    if response_image.status_code == 200:
                        image = Image.open(io.BytesIO(response_image.content))
                    else:
                        error_msg = f"Error al descargar imagen desde URL: {response_image.status_code}"
                        print(error_msg)
                        return False
                        
                else:
                    # Intentar obtener la primera entrada sin importar su nombre
                    print("Formato de respuesta no estándar, intentando extraer la imagen...")
                    for key, value in first_image.items():
                        if isinstance(value, str) and (value.startswith('http') or value.startswith('data:image')):
                            print(f"Encontrada posible imagen en clave: {key}")
                            
                            if value.startswith('http'):
                                response_image = requests.get(value, timeout=30)
                                image = Image.open(io.BytesIO(response_image.content))
                            else:  # Es base64
                                import base64
                                b64_data = value.split(',')[1] if ',' in value else value
                                image = Image.open(io.BytesIO(base64.b64decode(b64_data)))
                            break
                    else:
                        error_msg = f"No se encontró imagen en la respuesta: {first_image}"
                        print(error_msg)
                        return False
                
                # Guardar la imagen en formato WebP
                image.save(ruta_imagen, 'webp', quality=70)
                print(f"Imagen {imagen} guardada correctamente")
                return True
            else:
                error_msg = f"Respuesta inesperada de DeepInfra: {response_json}"
                print(error_msg)
                return False
                
    except Exception as e:
        print(f"Error al generar la imagen {imagen} con DeepInfra: {e}")
        return False

def procesar_fila(fila):
    imagen = fila["Imagen"]
    prompt = fila["Prompt"]
    return crear_imagen(imagen, prompt)

archivo_csv = "1. Imagenes.csv"
with open(archivo_csv, "r", newline="", encoding="utf-8") as archivo:
    lector = csv.DictReader(archivo)
    filas = list(lector)
    total_filas = len(filas)
    
        # Usar un número fijo de workers para DeepInfra para evitar sobrecargar la API
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_fila = {executor.submit(procesar_fila, fila): fila for fila in filas}
        with tqdm(total=total_filas, desc="Imágenes") as pbar:
            for future in concurrent.futures.as_completed(future_to_fila):
                future.result()
                pbar.update(1)
