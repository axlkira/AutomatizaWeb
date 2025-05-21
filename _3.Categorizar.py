import requests
import random
import csv
import json
import os

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
        start_index = content.find('</think>')
        if start_index != -1:
            return content[start_index+8:].strip()
        else:
            return content.strip()
    
    # CASO 1: Ollama local (sin API key requerida)
    if api_type == 'ollama':
        base_url = config.get('base_url', 'http://localhost:11434/v1')
        model = config.get('model', 'qwen3:8b')
        
        payload = {
            "model": model,
            "messages": prompt
        }
        url = f"{base_url}/chat/completions"
        print(f"Conectando a Ollama local: {url}")
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return extract_content(result['choices'][0]['message']['content'].strip())
    
    # CASO 2: OpenAI y compatibles (API-key en header)
    elif api_type == 'openai':
        try:
            import openai
            api_key = config.get('api_key')
            if not api_key and api_type != 'ollama':  # Solo Ollama no requiere API key
                raise ValueError(f"Se requiere API key para {api_type}")
                
            # Configurar cliente OpenAI
            openai.api_key = api_key
            if 'base_url' in config:
                openai.base_url = config['base_url']
                
            response = openai.ChatCompletion.create(
                model=config.get("model", "gpt-3.5-turbo"),
                messages=prompt
            )
            return extract_content(response.choices[0].message.content.strip())
        except ImportError:
            # Si no está instalado openai, usar requests
            return _generic_api_call(api_type, config, prompt, extract_content)
    
    # CASO 3: Cualquier otro proveedor (manejado genéricamente con headers de autorización)
    else:
        return _generic_api_call(api_type, config, prompt, extract_content)

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
    
    # Headers específicos para OpenRouter
    if api_type == 'openrouter':
        # OpenRouter requiere estos headers adicionales
        headers.update({
            "HTTP-Referer": "https://automatizaweb.local",  # Requerido por OpenRouter
            "X-Title": "AutomatizaWeb"  # Título de tu aplicación
        })
    
    # La mayoría de las APIs usan este formato de payload
    payload = {
        "model": model,
        "messages": prompt
    }
    
    # Configuración específica para OpenRouter
    if api_type == 'openrouter':
        # Asegurar que el modelo tiene el formato correcto para OpenRouter
        if not model.startswith('anthropic/') and not model.startswith('google/') and \
           not model.startswith('meta/') and not model.startswith('mistralai/') and not model.startswith('openai/'):
            # Si no tiene un prefijo de proveedor, intentar usar qwen como está en la configuración
            print(f"Usando modelo específico de OpenRouter: {model}")
        
        # Agregar transformers adicionales para OpenRouter
        payload["transforms"] = ["middle-out"]
        payload["route"] = "fallback"  # Usar fallback si la primera opción no está disponible
    
    # Añadir parámetros adicionales si están en la configuración
    if 'temperature' in config:
        payload["temperature"] = config.get('temperature')
    if 'max_tokens' in config:
        payload["max_tokens"] = config.get('max_tokens')
    
    url = f"{base_url}/chat/completions"
    print(f"Enviando solicitud a {api_type.capitalize()}: {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # Imprimir información detallada en caso de error
        if response.status_code != 200:
            print(f"ERROR {response.status_code}: {response.text}")
            
            # Manejo específico para errores de API key
            if response.status_code == 401:
                print("\n*** ERROR DE AUTENTICACIÓN ***")
                print("La API key no es válida o ha caducado.")
                print(f"Revisar la API key de {api_type} en config/ai_config.json")
                
                if api_type == 'openrouter':
                    # Intentar cambiar a un modelo alternativo si falla
                    alt_model = "google/gemini-pro"
                    print(f"\nIntentando con modelo alternativo: {alt_model}")
                    payload["model"] = alt_model
                    response = requests.post(url, json=payload, headers=headers)
            
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        print(f"Error al realizar petición: {e}")
        
        # Si estamos usando OpenRouter pero falla, intentar con Ollama local como plan B
        if api_type == 'openrouter':
            print("\n*** Intentando con Ollama local como alternativa ***")
            return _generic_api_call('ollama', 
                                    {"base_url": "http://localhost:11434/v1", "model": "qwen3:8b"}, 
                                    prompt, 
                                    extract_content)
        raise
    
    # Manejar diferentes formatos de respuesta
    try:
        if 'choices' in result and len(result['choices']) > 0:
            if 'message' in result['choices'][0]:
                return extract_content(result['choices'][0]['message']['content'].strip())
            elif 'text' in result['choices'][0]:
                return extract_content(result['choices'][0]['text'].strip())
    except Exception as e:
        print(f"Error procesando respuesta: {e}")
        print(f"Respuesta recibida: {result}")
    
    # Si llegamos aquí, la respuesta no tiene el formato esperado
    raise ValueError(f"Formato de respuesta no reconocido para {api_type}")

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
