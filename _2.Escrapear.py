import threading
import pandas as pd
import csv
from newspaper import Article
from concurrent.futures import ThreadPoolExecutor

csv_bloqueo = threading.Lock()

# Scrapeo de título y artículo (reintentando máximo 3 veces)
def escrapear_articulo(fila, urls_procesadas, columnas):
    url = fila['Ranking Url'].strip()
    if url in urls_procesadas or not url:
        return None
    for _ in range(3):
        try:
            articulo = Article(url)
            articulo.download()
            articulo.parse()
            titulo = articulo.title
            texto = articulo.text
            if titulo:
                columnas_existentes = [fila[col] for col in columnas]
                return columnas_existentes + [titulo, texto]
        except Exception as e:
            print(f"Error al extraer artículo: {e}")
    return None

# Configuración de archivos y manejo de URLs ya procesadas, verificando si el archivo de salida existe
df_scrapeado = None
urls_procesadas = set()
escribir_header = False
archivo_unificado, archivo_scrapeado = "1. Agrupados.csv", "2. Scrapeados.csv"
try:
    df_scrapeado = pd.read_csv(archivo_scrapeado, encoding='utf-8')
    urls_procesadas = set(df_scrapeado['Ranking Url'].dropna().str.strip())
except FileNotFoundError:
    urls_procesadas = set()
    escribir_header = True

# Lectura del archivo unificado, definición de columnas de salida y conteo de URLs totales
df_unificado = pd.read_csv(archivo_unificado, encoding='utf-8')
columnas_salida = list(df_unificado.columns) + ['Titulo', 'Articulo']
total_urls = len(df_unificado)

# Procesamiento concurrente de las URLs, extracción de artículos y escritura en el archivo de salida
with open(archivo_scrapeado, 'a', newline='', encoding='utf-8') as archivo:
    escritor = csv.writer(archivo)
    if escribir_header:
        escritor.writerow(columnas_salida)
    with ThreadPoolExecutor(max_workers=8) as ejecutor:
        resultados = ejecutor.map(lambda fila: escrapear_articulo(fila, urls_procesadas, df_unificado.columns), df_unificado.to_dict('records'))
        for count, datos in enumerate(filter(None, resultados), len(urls_procesadas) + 1):
            with csv_bloqueo:
                escritor.writerow(datos)
                archivo.flush()
            print(f"[{count}/{total_urls}] Artículo extraído de {datos[1]}")
