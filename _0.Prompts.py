import requests
from tqdm import tqdm
import random
import string
import json
import csv
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

imagenes_lock = threading.Lock()
redactados_lock = threading.Lock()

# Cargar prompts desde archivos JSON
prompt_prompt = json.load(open("_0. Prompts/0. Prompt.json", encoding="utf-8"))
alt_prompt = json.load(open("_0. Prompts/1. Alt.json", encoding="utf-8"))

def chat(pjson, reemplazos, api_type=None, api_config=None):
    """
    Función universal para interactuar con modelos de lenguaje.
    Totalmente dinámica, se adapta a cualquier proveedor configurado en ai_config.json.
    """
    # Preparar el prompt con los reemplazos
    prompt = [msg.copy() for msg in pjson]
    for mensaje in prompt:
        for clave, valor in reemplazos.items():
            if 'content' in mensaje:
                mensaje['content'] = mensaje['content'].replace(clave, valor)
                
    # Cargar la configuración desde el archivo
    config_path = os.path.join(os.path.dirname(__file__), 'config/ai_config.json')
    config_data = {
        "provider": "ollama",
        "models": {
            "ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen3:8b", "api_key": ""}
        }
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                print(f"Configuración cargada, usando proveedor: {config_data.get('provider')}")
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
    
    # Si no se especifica el tipo de API, usar el de la configuración
    if api_type is None:
        api_type = config_data.get("provider", "ollama")
    
    # Obtener configuración del proveedor seleccionado
    provider_config = config_data.get("models", {}).get(api_type, {})
    config = api_config or provider_config or {}
    
    print(f"Usando modelo de IA: {api_type} - {config.get('model', 'no especificado')}")
    
    # Función para procesar la respuesta y extraer el contenido
    def extract_content(content):
        start_index = content.find('<think>')
        if start_index != -1:
            return content[start_index+8:].strip()
        else:
            return content.strip()
    
    # Varios intentos en caso de error
    max_intentos = 3
    for intento in range(max_intentos):
        try:
            # CASO 1: Ollama local (sin API key requerida)
            if api_type == 'ollama':
                base_url = config.get('base_url', 'http://localhost:11434/v1')
                model = config.get('model', 'qwen3:8b')
                
                payload = {
                    "model": model,
                    "messages": prompt
                }
                url = f"{base_url}/chat/completions"
                
                response = requests.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return extract_content(result['choices'][0]['message']['content'].strip())
            
            # CASO 2: OpenAI y compatibles (API-key en header)
            elif api_type == 'openai':
                try:
                    import openai
                    from openai import OpenAI
                    
                    api_key = config.get('api_key')
                    if not api_key and api_type != 'ollama':  # Solo Ollama no requiere API key
                        raise ValueError(f"Se requiere API key para {api_type}")
                    
                    # Configurar cliente OpenAI
                    client = OpenAI(api_key=api_key)
                    if 'base_url' in config:
                        client.base_url = config['base_url']
                    
                    response = client.chat.completions.create(
                        model=config.get("model", "gpt-3.5-turbo"),
                        messages=prompt
                    )
                    return extract_content(response.choices[0].message.content)
                except ImportError:
                    # Si no está instalado openai, usar requests
                    return _generic_api_call(api_type, config, prompt, extract_content)
            
            # CASO 3: Cualquier otro proveedor (manejado genéricamente con headers de autorización)
            else:
                return _generic_api_call(api_type, config, prompt, extract_content)
                
        except Exception as e:
            print(f"Error en intento {intento+1}/{max_intentos}: {e}")
            if intento == max_intentos - 1:
                raise
            import time
            time.sleep(2)  # Esperar antes de reintentar

# Función auxiliar para llamadas genéricas a APIs
def _generic_api_call(api_type, config, prompt, extract_content):
    api_key = config.get('api_key')
    if not api_key and api_type != 'ollama':  # Solo Ollama no requiere API key
        raise ValueError(f"Se requiere API key para {api_type}")
        
    base_url = config.get('base_url', f"https://api.{api_type}.com/v1")
    model = config.get('model', f"{api_type}-chat")
    
    # La mayoría de las APIs usan este formato de headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # La mayoría de las APIs usan este formato de payload
    payload = {
        "model": model,
        "messages": prompt
    }
    
    # Añadir parámetros adicionales si están en la configuración
    if 'temperature' in config:
        payload["temperature"] = config.get('temperature')
    if 'max_tokens' in config:
        payload["max_tokens"] = config.get('max_tokens')
    
    url = f"{base_url}/chat/completions"
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    
    # Manejar diferentes formatos de respuesta
    try:
        if 'choices' in result and len(result['choices']) > 0:
            choice = result['choices'][0]
            if 'message' in choice:
                if isinstance(choice['message'], dict) and 'content' in choice['message']:
                    return extract_content(choice['message']['content'])
                else:
                    return extract_content(str(choice['message']))
            elif 'text' in choice:
                return extract_content(choice['text'])
        return extract_content(str(result))
    except Exception as e:
        print(f"Error al extraer contenido de la respuesta: {e}")
        return extract_content(str(result))

def limpiar_texto(texto):
    # Reemplazar comillas y saltos de línea
    texto = texto.replace('"', '').replace('\n', ' ').strip()
    
    # Extraer solo la descripción final si contiene el tag </think>
    if "</think>" in texto:
        texto = texto.split("</think>")[1].strip()
    
    # Formatear el texto agregando espacios después de signos de puntuación
    texto = re.sub(r'([.,;:!?])([^\s])', r'\1 \2', texto)
    
    # Separar palabras que están pegadas usando mayúsculas como referencia
    # Por ejemplo: convertir "AdetailedKeyboard" a "A detailed Keyboard"
    texto = re.sub(r'([a-z])([A-Z])', r'\1 \2', texto)
    
    # Reemplazar múltiples espacios con uno solo
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

def crear_imagen(titulo, slug):
    aleatorio = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    imagen = f"{slug}_{aleatorio}.webp"
    prompt = limpiar_texto(chat(prompt_prompt, {'{{titulo}}': titulo})).rstrip('.')
    alt = limpiar_texto(chat(alt_prompt, {'{{prompt}}': prompt})).rstrip('.')
    archivo_imagenes = "1. Imagenes.csv"
    with imagenes_lock:
        existe_csv = os.path.exists(archivo_imagenes)
        with open(archivo_imagenes, "a", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            if not existe_csv:
                escritor.writerow(["Imagen", "Prompt", "Alt"])
            escritor.writerow([imagen, prompt, alt])
            archivo.flush()
    return imagen, alt

def imagen_subtitulo(articulo, subtitulo, titulo, slug):
    imagen, alt = crear_imagen(f"{subtitulo} de {titulo}", slug)
    etiqueta = f'\n<center><img src="/wp-content/uploads/{imagen}" alt="{alt}"></center>\n'
    articulo = articulo.replace(f"<h2>{subtitulo}</h2>", f"<h2>{subtitulo}</h2>{etiqueta}")
    return articulo

def agregar_imagenes(articulo, titulo, slug):
    subtitulos = []
    posicion = 0
    while True:
        inicio = articulo.find('<h2>', posicion)
        if inicio == -1:
            break
        final = articulo.find('</h2>', inicio)
        if final == -1:
            break
        subtitulo = articulo[inicio + len('<h2>'):final]
        subtitulos.append((inicio, final, subtitulo))
        posicion = final + len('</h2>')
    
    total_subtitulos = len(subtitulos)
    if total_subtitulos > 0:
        indices_imagenes = [
            subtitulos[min(int(total_subtitulos * 0.33), total_subtitulos - 1)],
            subtitulos[min(int(total_subtitulos * 0.66), total_subtitulos - 1)]
        ]
        for indice, (inicio, final, subtitulo) in enumerate(indices_imagenes):
            articulo = imagen_subtitulo(articulo, subtitulo, titulo, slug)
    imagen, alt = crear_imagen(titulo, slug)
    return articulo, imagen, alt

def leer_csv(ruta_archivo):
    with open(ruta_archivo, "r", newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))

def obtener_filas_existentes(ruta_archivo):
    filas_existentes = set()
    if os.path.exists(ruta_archivo):
        filas = leer_csv(ruta_archivo)
        filas_existentes = {fila["Titulo"] for fila in filas}
    return filas_existentes

def procesar_fila(fila, ruta_archivo, nombres_columnas):
    titulo = fila["Titulo"]
    slug = fila["SLUG"]
    articulo = fila["Articulo"]
    articulo, portada, alt = agregar_imagenes(articulo, titulo, slug)
    fila.update({"Articulo": articulo, "Portada": portada, "Alt": alt})
    with redactados_lock:
        existe_csv = os.path.exists(ruta_archivo)
        with open(ruta_archivo, "a", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=nombres_columnas)
            if not existe_csv:
                escritor.writeheader()
            escritor.writerow(fila)
            archivo.flush()

origen = "4. Redactados.csv"  # Archivo correcto de entrada
destino = "4. Redactados[IMGs].csv"  # Archivo de salida con mejor formato
filas = leer_csv(origen)
""" //nombres_columnas = list(filas[0].keys()) + ["Portada"] """
nombres_columnas = list(filas[0].keys()) + ["Portada", "Alt"]
filas_existentes = obtener_filas_existentes(destino)
filas_a_procesar = [fila for fila in filas if fila["Titulo"] not in filas_existentes]
with ThreadPoolExecutor(max_workers=1) as executor:
    futures = [executor.submit(procesar_fila, fila, destino, nombres_columnas) 
              for fila in filas_a_procesar]
    with tqdm(total=len(filas_a_procesar), desc="Articulos") as pbar:
        for future in as_completed(futures):
            future.result()
            pbar.update(1)
