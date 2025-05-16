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
            df = df.tail(10)  # Mostrar más artículos
            
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
    if script not in ['_0.Fusionar.py', '_1.Agrupar.py', '_2.Escrapear.py', '_3.Categorizar.py', '_4.Redactar.py']:
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
    return send_from_directory(app.template_folder, 'index.html')

# Ruta para obtener la configuración de IA
@app.route('/api/config/ai', methods=['GET'])
def get_ai_config():
    try:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/ai_config.json'))
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Por seguridad, no devolver API keys en la respuesta
            safe_config = config.copy()
            for provider, settings in safe_config['models'].items():
                if 'api_key' in settings and settings['api_key']:
                    settings['api_key'] = '********'
            return jsonify(safe_config)
        else:
            return jsonify({"error": "Archivo de configuración no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para actualizar la configuración de IA
@app.route('/api/config/ai', methods=['POST'])
def update_ai_config():
    try:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/ai_config.json'))
        current_config = {}
        
        # Leer configuración actual si existe
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                current_config = json.load(f)
        
        # Obtener datos enviados
        data = request.json
        
        # Validar datos mínimos requeridos
        if 'provider' not in data:
            return jsonify({"error": "Falta el proveedor"}), 400
            
        # Si se envía un nuevo API key, actualizar, sino mantener el actual
        if data['provider'] in current_config['models']:
            provider_config = data.get('config', {})
            
            # Solo actualizar API key si se proporciona uno nuevo y no está vacío
            if 'api_key' in provider_config and provider_config['api_key'] != '********' and provider_config['api_key'].strip():
                current_config['models'][data['provider']]['api_key'] = provider_config['api_key']
                
            # Actualizar URL base si se proporciona
            if 'base_url' in provider_config and provider_config['base_url'].strip():
                current_config['models'][data['provider']]['base_url'] = provider_config['base_url']
                
            # Actualizar modelo si se proporciona
            if 'model' in provider_config and provider_config['model'].strip():
                current_config['models'][data['provider']]['model'] = provider_config['model']
        
        # Actualizar proveedor activo
        current_config['provider'] = data['provider']
        
        # Guardar configuración actualizada
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2)
            
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
