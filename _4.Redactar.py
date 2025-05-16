from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import unicodedata
import markdown2
import json
import csv
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Leer categorías desde archivo txt
categorias = ", ".join(f"{i}" for i in open("3. Categorias.txt", encoding="utf-8").read().splitlines())

# Cargar prompts desde archivos JSON
resumen_prompt = json.load(open("_1.Prompts/1.Resumen.json", encoding="utf-8"))
titulo_prompt = json.load(open("_1.Prompts/2.Titulo.json", encoding="utf-8"))
articulo_prompt = json.load(open("_1.Prompts/3.Articulo.json", encoding="utf-8"))
descripcion_prompt = json.load(open("_1.Prompts/4.Descripcion.json", encoding="utf-8"))
categoria_prompt = json.load(open("_1.Prompts/5.Categoria.json", encoding="utf-8"))

csv_bloqueo = Lock()

def chat(pjson, reemplazos, api_type='ollama', api_config=None):
    """
    Función universal para interactuar con modelos de lenguaje via Ollama o OpenAI.
    Por defecto usa Ollama local con el modelo qwen3:8b.
    """
    prompt = [msg.copy() for msg in pjson]
    for mensaje in prompt:
        for clave, valor in reemplazos.items():
            if 'content' in mensaje:
                mensaje['content'] = mensaje['content'].replace(clave, valor)

    if api_type == 'ollama':
        config = api_config or {'base_url': 'http://localhost:11434/v1', 'model': 'qwen3:8b'}
        payload = {
            "model": config.get("model", "qwen3:8b"),
            "messages": prompt
        }
        url = f"{config.get('base_url', 'http://localhost:11434/v1')}/chat/completions"
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        start_index = content.find('</think>')
        if start_index != -1:
            return content[start_index+8:].strip()
        else:
            return content.strip()

    elif api_type == 'openai':
        import openai
        config = api_config or {}
        openai.api_key = config.get('api_key')
        if 'base_url' in config:
            openai.base_url = config['base_url']
        response = openai.ChatCompletion.create(
            model=config.get("model", "gpt-3.5-turbo"),
            messages=prompt
        )
        content = response.choices[0].message.content.strip()
        start_index = content.find('</think>')
        if start_index != -1:
            return content[start_index+8:].strip()
        else:
            return content.strip()
    else:
        raise ValueError(f"API type {api_type} no soportada.")

def limpiar_linea(texto):
    return ' '.join(re.sub(r'["\'\`\n\t]', '', texto).split()).strip()

def crear_resumen(titulo, articulo):
    return limpiar_linea(chat(resumen_prompt, {'{titulo}': titulo, '{articulo}': articulo}))

def crear_titulo(resumen, keywords):
    return limpiar_linea(chat(titulo_prompt, {'{resumen}': resumen, '{keywords}': keywords})).rstrip(".")

def crear_articulo(resumen, keywords, titulo):
    articulo = chat(articulo_prompt, {'resumen': resumen, '{keywords}': keywords, '{titulo}': titulo})
    soup = BeautifulSoup(markdown2.markdown(articulo), 'html.parser')
    for tag, texto in [('h1', None), ('h2', 'Introducción')]:
        elemento = soup.find(tag, string=texto) if texto else soup.find(tag)
        if elemento:
            elemento.decompose()
    articulo = re.sub(r'En (?:conclusión|resumen)(.*)', '', str(soup), flags=re.IGNORECASE|re.DOTALL)
    return articulo.strip()

def crear_descripcion(resumen, titulo):
    return limpiar_linea(chat(descripcion_prompt, {'{resumen}': resumen, '{titulo}': titulo}))

def crear_categoria(titulo):
    return limpiar_linea(chat(categoria_prompt, {'{categorias}': categorias, '{titulo}': titulo})).rstrip(".")

def crear_slug(keywords):
    keyword = min(keywords.splitlines(), key=len).lower()
    normalized = unicodedata.normalize('NFKD', keyword).encode('ASCII', 'ignore').decode().replace(' ', '-')
    return re.sub(r'[^\w-]', '', normalized)

def leer_keywords(nombre_archivo, es_existente=True):
    if not os.path.exists(nombre_archivo):
        return set() if es_existente else []
    with open(nombre_archivo, newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        return {fila['Keywords'] for fila in lector} if es_existente else list(lector)

# Definición de la función para procesar cada fila de datos, generando el contenido completo
def procesar_fila(fila):
    keywords = fila['Keywords'].strip()
    keywords_linea = ', '.join(f"{k}" for k in keywords.split('\n'))
    resumen = crear_resumen(fila['Titulo'].strip(), fila['Articulo'].strip())
    titulo = crear_titulo(resumen, keywords_linea)
    return [
        keywords,
        resumen,
        titulo,
        crear_articulo(resumen, keywords_linea, titulo),
        crear_descripcion(resumen, titulo),
        crear_categoria(titulo),
        crear_slug(keywords)
    ]

# Lectura de datos existentes, filtrado de filas a procesar y ejecución concurrente con escritura en CSV
scrapeado = leer_keywords("2. Scrapeados.csv", es_existente=False)
keywords_existentes = leer_keywords("4. Redactados.csv")
filas_a_procesar = [reg for reg in scrapeado if reg['Keywords'].strip() not in keywords_existentes]

with open("4. Redactados.csv", "a", newline="", encoding="utf-8") as archivo_csv:
    escritor = csv.writer(archivo_csv)
    if archivo_csv.tell() == 0:
        escritor.writerow(["Keywords", "Titulo", "Articulo", "Descripcion", "Categorias", "SLUG"])
        archivo_csv.flush()
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = {executor.submit(procesar_fila, fila): fila for fila in filas_a_procesar}
        with tqdm(total=len(futures), desc="Artículos") as pbar:
            for future in as_completed(futures):
                try:
                    resultado = future.result()
                    with csv_bloqueo:
                        escritor.writerow(resultado)
                        archivo_csv.flush()
                except Exception as e:
                    print(f"Error procesando fila: {e}")
                finally:
                    pbar.update(1)


