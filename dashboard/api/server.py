from flask import Flask, jsonify, request, send_from_directory, render_template
from werkzeug.utils import secure_filename
import pandas as pd
import os
import sys
import subprocess
import json

app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Configurar CORS para permitir peticiones desde el frontend
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Ruta para obtener estadísticas
@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = {
        'articulos_generados': 0,
        'urls_procesadas': 0,
        'categorias': 0,
        'pendientes': 0
    }
    
    # Ruta base - directorio principal de AutomatizaWeb
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    
    # Contar artículos generados
    try:
        articulos_path = os.path.join(base_dir, "4. Redactados.csv")
        if os.path.exists(articulos_path):
            df = pd.read_csv(articulos_path)
            stats['articulos_generados'] = len(df)
            print(f"Encontrados {stats['articulos_generados']} artículos en {articulos_path}")
    except Exception as e:
        print(f"Error al leer artículos: {e}")
    
    # Contar URLs procesadas
    try:
        scrapeados_path = os.path.join(base_dir, "2. Scrapeados.csv")
        if os.path.exists(scrapeados_path):
            df = pd.read_csv(scrapeados_path)
            stats['urls_procesadas'] = len(df)
            print(f"Encontradas {stats['urls_procesadas']} URLs en {scrapeados_path}")
    except Exception as e:
        print(f"Error al leer URLs: {e}")
    
    # Contar categorías
    try:
        categorias_path = os.path.join(base_dir, "3. Categorias.txt")
        if os.path.exists(categorias_path):
            with open(categorias_path, "r", encoding="utf-8") as f:
                categorias = f.readlines()
                stats['categorias'] = len(categorias)
                print(f"Encontradas {stats['categorias']} categorías en {categorias_path}")
    except Exception as e:
        print(f"Error al leer categorías: {e}")
    
    # Calcular pendientes
    try:
        agrupados_path = os.path.join(base_dir, "1. Agrupados.csv")
        scrapeados_path = os.path.join(base_dir, "2. Scrapeados.csv")
        if os.path.exists(agrupados_path) and os.path.exists(scrapeados_path):
            df_agrupados = pd.read_csv(agrupados_path)
            df_scrapeados = pd.read_csv(scrapeados_path)
            stats['pendientes'] = len(df_agrupados) - len(df_scrapeados)
            if stats['pendientes'] < 0:
                stats['pendientes'] = 0
            print(f"Calculados {stats['pendientes']} pendientes")
    except Exception as e:
        print(f"Error al calcular pendientes: {e}")
    
    return jsonify(stats)

# Ruta para obtener artículos recientes
@app.route('/api/articulos', methods=['GET'])
def get_articulos():
    articulos = []
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        articulos_path = os.path.join(base_dir, "4. Redactados.csv")
        
        if os.path.exists(articulos_path):
            df = pd.read_csv(articulos_path)
            # Ordenar por las filas más recientes (asumiendo que las últimas filas son las más recientes)
            # No limitamos la cantidad de artículos para que se muestren todos en DataTables
            
            for _, row in df.iterrows():
                # Asegurarse de que todas las columnas existan o usar valores por defecto
                articulo = {
                    'keyword': row.get('Keywords', ''),
                    'titulo': row.get('Titulo', ''),
                    'categoria': row.get('Categorias', ''),
                    'slug': row.get('SLUG', ''),
                    'id': str(_)  # Añadir un ID para referencia
                }
                articulos.append(articulo)
                
            print(f"Cargados {len(articulos)} artículos recientes de {articulos_path}")
    except Exception as e:
        print(f"Error al leer artículos: {e}")
    
    return jsonify(articulos)

# Ruta para ejecutar scripts
@app.route('/api/ejecutar', methods=['POST'])
def ejecutar_script():
    data = request.json
    script = data.get('script')
    
    # Validar solo los scripts existentes
    if script not in ['_0.Fusionar.py', '_01.Descanivalizador.py', '_1.Agrupar.py', '_2.Escrapear.py', '_3.Categorizar.py', '_4.Redactar.py']:
        return jsonify({'error': 'Script no permitido'}), 400
    
    try:
        # Ruta base - directorio principal de AutomatizaWeb
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        
        # Comprobar si el script realmente existe
        script_path = os.path.join(base_dir, script)
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': f"El archivo {script} no existe en {base_dir}"
            }), 404
            
        print(f"Ejecutando: {script} en {base_dir}")
        
        # Ejecutar el script en el directorio base (donde están los archivos originales)
        resultado = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=base_dir  # Ejecutar en el directorio correcto
        )
        
        return jsonify({
            'success': resultado.returncode == 0,
            'output': resultado.stdout,
            'error': resultado.stderr
        })
    except Exception as e:
        import traceback
        error_detallado = traceback.format_exc()
        print(f"Error al ejecutar script: {error_detallado}")
        return jsonify({'error': str(e), 'traceback': error_detallado}), 500

# Ruta para descargar el archivo de redactados
@app.route('/api/descargar-redactados')
def descargar_redactados():
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        file_path = os.path.join(base_dir, "4. Redactados.csv")
        
        if os.path.exists(file_path):
            # Enviar el archivo para descarga
            return send_from_directory(directory=base_dir, path="4. Redactados.csv", as_attachment=True)
        else:
            return jsonify({"error": "El archivo no existe"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para obtener el progreso del script Redactar
@app.route('/api/progreso/<script>')
def get_progreso(script):
    if script == "_4.Redactar.py":
        try:
            # Leer el progreso desde el archivo temporal
            progreso_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')), 'progreso_redactar.txt')
            if os.path.exists(progreso_file):
                with open(progreso_file, 'r') as f:
                    progreso = int(f.read().strip())
                return jsonify({"progreso": progreso})
            else:
                return jsonify({"progreso": 0})
        except Exception as e:
            print(f"Error al leer progreso: {e}")
            return jsonify({"progreso": 0})
    return jsonify({"progreso": 0})

# Ruta para obtener un artículo completo por su ID
@app.route('/api/articulo/<id>')
def get_articulo(id):
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        articulos_path = os.path.join(base_dir, "4. Redactados.csv")
        
        if os.path.exists(articulos_path):
            df = pd.read_csv(articulos_path)
            # Convertir ID a índice numérico
            try:
                indice = int(id)
                if 0 <= indice < len(df):
                    articulo = {
                        'keyword': df.iloc[indice].get('Keywords', ''),
                        'titulo': df.iloc[indice].get('Titulo', ''),
                        'articulo': df.iloc[indice].get('Articulo', ''),
                        'descripcion': df.iloc[indice].get('Descripcion', ''),
                        'categoria': df.iloc[indice].get('Categorias', '') or df.iloc[indice].get('Categoria', ''),
                        'slug': df.iloc[indice].get('SLUG', '') or df.iloc[indice].get('Slug', ''),
                    }
                    return jsonify(articulo)
            except Exception as e:
                print(f"Error al procesar índice: {e}")
        
        return jsonify({"error": "Artículo no encontrado"}), 404
    except Exception as e:
        print(f"Error al buscar artículo: {e}")
        return jsonify({"error": str(e)}), 500

# Ruta principal para servir la aplicación
@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

# Ruta para la sección de artículos
@app.route('/articulos')
def articulos():
    return send_from_directory(app.template_folder, 'index.html')

# Ruta para la sección de scraping
@app.route('/scraping')
def scraping():
    return send_from_directory(app.template_folder, 'index.html')

# Ruta para la sección de configuración
@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')

# ENDPOINT SEGURO PARA OBTENER LA CONFIGURACIÓN DE APIS
@app.route('/api/config', methods=['GET'])
def get_api_config():
    try:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/ai_config.json'))
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Por seguridad, oculta las API keys reales
            safe_config = json.loads(json.dumps(config))
            # Oculta API keys en image_generators
            if 'image_generators' in safe_config:
                for gen, conf in safe_config['image_generators'].items():
                    if isinstance(conf, dict) and 'api_key' in conf and conf['api_key']:
                        safe_config['image_generators'][gen]['api_key'] = '********'
            # Oculta API keys en other_apis
            if 'other_apis' in safe_config:
                for api, conf in safe_config['other_apis'].items():
                    if isinstance(conf, dict) and 'api_key' in conf and conf['api_key']:
                        safe_config['other_apis'][api]['api_key'] = '********'
            return jsonify(safe_config)
        else:
            return jsonify({"error": "Archivo de configuración no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ENDPOINT SEGURO PARA ACTUALIZAR LA CONFIGURACIÓN DE APIS
@app.route('/api/config', methods=['POST'])
def update_api_config():
    try:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/ai_config.json'))
        if not os.path.exists(config_path):
            return jsonify({"error": "Archivo de configuración no encontrado"}), 404
        
        # Leer configuración actual
        with open(config_path, 'r', encoding='utf-8') as f:
            current_config = json.load(f)
        
        # Obtener datos del request
        data = request.json
        print("Datos recibidos para guardar:", data)
        
        # Validar estructura básica del nuevo formato
        if not isinstance(data, dict):
            return jsonify({"error": "Configuración inválida: no es un objeto JSON"}), 400
        
        # Actualizar provider y models
        if 'provider' in data:
            current_config['provider'] = data['provider']
        
        if 'models' in data and isinstance(data['models'], dict):
            # Si no existe, inicializar
            if 'models' not in current_config:
                current_config['models'] = {}
            
            # Actualizar cada modelo
            for provider, model_data in data['models'].items():
                current_config['models'][provider] = model_data
        
        # Actualizar configuraciones de imagen y video
        if 'image_api_key' in data:
            current_config['image_api_key'] = data['image_api_key']
        
        if 'video_api_key' in data:
            current_config['video_api_key'] = data['video_api_key']
            
        # Actualizar proveedor de imagen y modelo si está presente
        if 'image_provider' in data:
            current_config['image_provider'] = data['image_provider']
            
        if 'image_model' in data:
            current_config['image_model'] = data['image_model']
        
        # Guardar configuración actualizada
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2, ensure_ascii=False)
        return jsonify({"success": True, "message": "Configuración actualizada correctamente"})
    except Exception as e:
        import traceback
        error_detallado = traceback.format_exc()
        print(f"Error al actualizar configuración: {error_detallado}")
        return jsonify({"error": str(e), "traceback": error_detallado}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

# Endpoint para subir archivos CSV a la carpeta _0.CSVs
@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    try:
        # Verifica que haya archivos en la petición
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'No se encontraron archivos en la petición (campo files)'}), 400
        files = request.files.getlist('files')
        if not files:
            return jsonify({'success': False, 'error': 'No se enviaron archivos'}), 400
        # Carpeta destino
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        dest_dir = os.path.join(base_dir, '_0.CSVs')
        os.makedirs(dest_dir, exist_ok=True)
        saved_files = []
        for file in files:
            filename = secure_filename(file.filename)
            if not filename.lower().endswith('.csv'):
                return jsonify({'success': False, 'error': f'El archivo {filename} no es un CSV'}), 400
            file.save(os.path.join(dest_dir, filename))
            saved_files.append(filename)
        return jsonify({'success': True, 'files': saved_files, 'message': 'Archivos subidos correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ollama/models', methods=['GET'])
def get_ollama_models():
    try:
        # Ejecuta 'ollama list' y parsea la salida de texto
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'error': 'No se pudo obtener la lista de modelos de Ollama', 'details': result.stderr}), 500
        lines = result.stdout.strip().splitlines()
        modelos = []
        for line in lines:
            # Normalmente: nombre  tamaño  fecha
            parts = line.split()
            if len(parts) > 0 and not line.lower().startswith('modelo'):
                modelos.append(parts[0])
        return jsonify({'modelos': modelos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/openai/models', methods=['POST'])
def get_openai_models():
    try:
        data = request.json
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({'error': 'Se requiere API key'}), 400
        
        # Consultar la API de OpenAI para obtener modelos disponibles
        import requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get('https://api.openai.com/v1/models', headers=headers)
        
        if response.status_code == 200:
            models_data = response.json()
            # Filtrar solo modelos de chat GPT
            chat_models = [model['id'] for model in models_data['data'] 
                          if 'gpt' in model['id'] and not model['id'].startswith('gpt-3.5-turbo-') 
                          and not model['id'].startswith('gpt-4-') and not '-vision-' in model['id']]
            return jsonify({'modelos': chat_models})
        else:
            return jsonify({'error': f'Error al consultar la API de OpenAI: {response.text}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/deepseek/models', methods=['POST'])
def get_deepseek_models():
    try:
        data = request.json
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({'error': 'Se requiere API key'}), 400
        
        # DeepSeek no tiene endpoint para listar modelos, devolvemos lista predefinida
        # pero validamos la API key
        import requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        # Hacemos una prueba de validación de API key con una petición mínima
        # A un endpoint conocido
        test_data = {
            'model': 'deepseek-chat',
            'messages': [{'role': 'user', 'content': 'test'}],
            'max_tokens': 1
        }
        
        # Esta petición solo es para validar la API key
        response = requests.post('https://api.deepseek.com/v1/chat/completions', 
                                json=test_data, headers=headers)
        
        if response.status_code in [200, 401, 429]:
            # Si la API key es válida o hay error de cuota/límites, devolvemos los modelos
            deepseek_models = ['deepseek-chat', 'deepseek-coder', 'deepseek-v2']
            return jsonify({'modelos': deepseek_models})
        else:
            return jsonify({'error': f'API key de DeepSeek inválida: {response.text}'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/openrouter/models', methods=['POST'])
def get_openrouter_models():
    try:
        data = request.json
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({'error': 'Se requiere API key'}), 400
        
        # Consultar la API de OpenRouter para obtener modelos disponibles
        import requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'HTTP-Referer': 'https://automatizaweb.app'
        }
        response = requests.get('https://openrouter.ai/api/v1/models', headers=headers)
        
        if response.status_code == 200:
            models_data = response.json()
            # Obtener solo los IDs de modelos de chat
            chat_models = [model['id'] for model in models_data['data'] 
                          if model.get('context_length', 0) > 4000]
            return jsonify({'modelos': chat_models})
        else:
            return jsonify({'error': f'Error al consultar la API de OpenRouter: {response.text}'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/grok/models', methods=['POST'])
def get_grok_models():
    try:
        data = request.json
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({'error': 'Se requiere API key'}), 400
        
        # Consultar la API de X.AI (Grok) para obtener modelos disponibles
        import requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # X.AI no tiene endpoint de listado de modelos, así que probamos validar la API key
        test_data = {
            'model': 'grok-3-mini-fast-latest',
            'messages': [{'role': 'user', 'content': 'test'}],
            'max_tokens': 1
        }
        
        # Solo para validar la API key
        response = requests.post('https://api.x.ai/v1/chat/completions', 
                                json=test_data, headers=headers)
        
        if response.status_code in [200, 429]:
            # Si la API key es válida, devolvemos los modelos conocidos
            grok_models = ['grok-3-mini-fast-latest', 'grok-3-mini-latest', 'grok-3-lean-latest', 'grok-1.5-turbo']
            return jsonify({'modelos': grok_models})
        else:
            return jsonify({'error': f'API key de Grok inválida: {response.text}'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para obtener modelos disponibles de DeepInfra
@app.route('/api/deepinfra/models', methods=['POST'])
def get_deepinfra_models():
    try:
        # Obtener la API key del request
        data = request.json
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({'error': 'API key requerida para consultar modelos de DeepInfra'}), 400
        
        # Intentar validar la API key de DeepInfra
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # En este caso podemos intentar obtener los modelos disponibles de DeepInfra
        # consultando su API, pero como alternativa simple vamos a devolver una lista predefinida
        # Podríamos usar: https://api.deepinfra.com/v1/models
        
        modelos = [
            'stabilityai/sd3.5-medium',
            'stabilityai/sd3.5-large',
            'stable-diffusion-xl-turbo',
            'stable-diffusion-xl-base-1.0',
            'segmind/midjourney-v5',
            'segmind/midjourney-v6',
            'playground/v2.5',
            '01-ai/yi-image-2.0-1b',
            'anthropic/claude-3.5-sonnet',
            'jina/midjourney-4',
            'laion/erlich',
            'segmind/ssd-1b-anime'
        ]
        
        # Podríamos validar la API key haciendo una solicitud simple
        try:
            test_url = 'https://api.deepinfra.com/v1/openai/images/generations'
            test_payload = {
                'prompt': 'test',
                'model': 'stabilityai/sd3.5-medium',
                'n': 1,
                'size': '256x256'
            }
            response = requests.post(test_url, headers=headers, json=test_payload, timeout=5)
            
            # Si hay un error de autenticación, DeepInfra devolverá un 401
            if response.status_code == 401:
                return jsonify({'error': 'API key inválida para DeepInfra'}), 401
                
        except Exception as e:
            print(f"Error al validar API key de DeepInfra: {str(e)}")
            # Continuamos de todas formas y devolvemos los modelos predefinidos
        
        return jsonify({'modelos': modelos})
        
    except Exception as e:
        import traceback
        error_detallado = traceback.format_exc()
        print(f"Error al obtener modelos de DeepInfra: {error_detallado}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
