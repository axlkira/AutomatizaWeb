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
def cargar_configuracion_apis():
    config_path = os.path.join("config", "ai_config.json")
    if not os.path.exists(config_path):
        # Config por defecto (Fooocus)
        return ["http://localhost:8888/v1/generation/text-to-image"], "fooocus"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    # Buscar generador activo
    image_generators = config.get("image_generators", {})
    active = config.get("active_image_generator") or image_generators.get("default", "fooocus")
    generator_conf = image_generators.get(active, {})
    base_urls = generator_conf.get("base_urls")
    if not base_urls:
        base_urls = ["http://localhost:8888/v1/generation/text-to-image"]
    return base_urls, active

fooocus_base_urls, generador_activo = cargar_configuracion_apis()
url_cycle = itertools.cycle(fooocus_base_urls)

url_lock = Lock()
# --- Fin configuración dinámica de APIs ---

def crear_imagen(imagen, prompt):
    ruta_imagen = os.path.join(IMGS, imagen)
    if os.path.exists(ruta_imagen):
        return True
    
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": prompt,
        "negative_prompt": "worst quality, low quality, normal quality, lowres, low details, oversaturated, undersaturated, overexposed, underexposed, grayscale, bw, bad photo, bad photography, bad art, watermark, signature, text font, username, error, logo, words, letters, digits, autograph, trademark, name, blur, blurry, censored, jpeg artifacts, ugly, repetition, poorly drawn, mutilated, poorly lit, bad shadow, draft, cropped, out of frame, cut off, censored, jpeg artifacts, out of focus, glitch, duplicate, airbrushed, cartoon, anime, semi-realistic, cgi, render, blender, digital art, manga, amateur, 3D, 3D Game Scene, 3D Character, bad hands, bad anatomy, bad face, bad body, bad feet, bad teeth, bad arms, bad legs, deformities, nudity, naked, nude, penis, dick, cock, vagina, pussy, vulva, breasts, boobs, tits, bare chest, exposed genitals, topless, bottomless",
        "aspect_ratios_selection": "1280*720",
        "performance_selection": "Speed",
        "image_number": 1,
        "style_selections": ["Fooocus Enhance", "Fooocus V2", "Fooocus Sharp"]
    }
    
    with url_lock:
        fooocus_base_url = next(url_cycle)
        response = requests.post(fooocus_base_url, headers=headers, json=data)
        response_json = response.json()
        url_devuelta = response_json[0]["url"]
        original_url = urlparse(fooocus_base_url)
        parsed_returned_url = urlparse(url_devuelta)
        
        if original_url.port != parsed_returned_url.port:
            url_devuelta = urlunparse(parsed_returned_url._replace(netloc=f"{parsed_returned_url.hostname}:{original_url.port}"))
    
    response_image = requests.get(url_devuelta)
    try:
        image = Image.open(io.BytesIO(response_image.content))
        image.save(ruta_imagen, 'webp', quality=70)
        return True
    except Exception as e:
        print(f"Error al generar la imagen {imagen}: {e}")
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
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(fooocus_base_urls)*2) as executor:
        future_to_fila = {executor.submit(procesar_fila, fila): fila for fila in filas}
        with tqdm(total=total_filas, desc="Imágenes") as pbar:
            for future in concurrent.futures.as_completed(future_to_fila):
                future.result()
                pbar.update(1)
