from flask import Flask, jsonify, request, send_from_directory, render_template
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

# Ruta para obtener el progreso del script Redactar (simulado por ahora)
@app.route('/api/progreso/<script>')
def get_progreso(script):
    # En una implementación real, esto podría leer un archivo de estado o una base de datos
    if script == "_4.Redactar.py":
        # Simular progreso aleatorio entre 0-100% para pruebas
        # En una implementación real, leerías el progreso real del script
        import random
        progreso = random.randint(0, 100) if random.random() > 0.8 else 100
        return jsonify({"progreso": progreso})
    return jsonify({"progreso": 0})

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

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
