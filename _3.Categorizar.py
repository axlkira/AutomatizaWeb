import requests
import random
import csv
import json

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

# Carga de los títulos desde el archivo CSV y selección de una muestra aleatoria de hasta 100 elementos
titulos = []
with open("2. Scrapeados.csv", encoding="utf-8") as f:
    titulos = [row['Titulo'] for row in csv.DictReader(f)]
titulos = random.sample(titulos, min(100, len(titulos)))

# Carga del prompt desde el archivo JSON
with open("_1.Prompts/0.Categorias.json", encoding="utf-8") as f:
    prompt = json.load(f)

# Llamada a la función chat para generar las categorías, pasando el prompt y los reemplazos necesarios
categorias = chat(prompt, {'{titulos}': "\n".join(titulos)})

# Limpieza de la respuesta de la IA y guardado en un archivo de texto, eliminando prefijos y espacios innecesarios
categorias_limpias = "\n".join(line.lstrip("- ").strip() for line in categorias.splitlines() if line)
with open("3. Categorias.txt", 'w', encoding="utf-8") as f:
    f.write(categorias_limpias)
