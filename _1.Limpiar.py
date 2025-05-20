import csv
import os
import re

def extraer_imagenes_de_articulo(articulo):
    patron = r'<img\s+[^>]*src=["\']/wp-content/uploads/(.*?\.webp)["\']'
    return set(re.findall(patron, articulo))

archivo_imagenes = "1. Imagenes.csv"
archivo_redactados = "4. Redactados[IMGs].csv"
imagenes_usadas = set()

# Verificar qué imágenes están siendo utilizadas en los artículos redactados
if os.path.exists(archivo_redactados):
    with open(archivo_redactados, "r", encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            if fila.get('Portada'):
                imagenes_usadas.add(fila['Portada'].strip())
            if fila.get('Articulo'):
                imagenes_articulo = extraer_imagenes_de_articulo(fila['Articulo'])
                imagenes_usadas.update(imagenes_articulo)

# Obtener todas las imágenes registradas
imagenes_registradas = []
if os.path.exists(archivo_imagenes):
    with open(archivo_imagenes, "r", encoding='utf-8') as f:
        lector = csv.DictReader(f)
        imagenes_registradas = list(lector)

# Identificar imágenes que no están completas (sin Alt o Prompt)
imagenes_incompletas = []
imagenes_completas = []
for imagen in imagenes_registradas:
    if not imagen.get('Alt') or not imagen.get('Prompt') or imagen.get('Alt').strip() == "" or imagen.get('Prompt').strip() == "":
        if imagen.get('Imagen') not in imagenes_usadas:
            imagenes_incompletas.append(imagen)
        else:
            # Si la imagen está incompleta pero ya está usada en un artículo,
            # la mantenemos pero completamos los campos vacíos
            if not imagen.get('Alt') or imagen.get('Alt').strip() == "":
                imagen['Alt'] = "Imagen descriptiva"
            if not imagen.get('Prompt') or imagen.get('Prompt').strip() == "":
                imagen['Prompt'] = "Descripción de la imagen"
            imagenes_completas.append(imagen)
    else:
        imagenes_completas.append(imagen)

# Mostrar estadísticas
print(f"Total de imágenes: {len(imagenes_registradas)}")
print(f"Imágenes incompletas: {len(imagenes_incompletas)}")
print(f"Imágenes usadas en artículos: {len(imagenes_usadas)}")

# Eliminar imágenes incompletas que no se están usando
if imagenes_incompletas:
    print(f"Eliminando {len(imagenes_incompletas)} imágenes incompletas...")
    # Reescribir el archivo de imágenes solo con las completas
    with open(archivo_imagenes, "w", newline="", encoding='utf-8') as f:
        campos = ["Imagen", "Prompt", "Alt"]
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        for imagen in imagenes_completas:
            escritor.writerow(imagen)
    print("Limpieza completada.")
else:
    print("No hay imágenes incompletas para eliminar.")

# Verificar el archivo destino (4. Redactados[IMGs].csv) para asegurarse de que tiene todos los campos necesarios
# En caso de error con campo 'Alt' que vimos en la ejecución de _0.Prompts.py
if os.path.exists(archivo_redactados):
    filas_originales = []
    encabezados = []
    
    # Leer el archivo original
    with open(archivo_redactados, "r", encoding='utf-8') as f:
        lector = csv.reader(f)
        encabezados = next(lector)  # Leer encabezados
        
        # Verificar si faltan campos necesarios
        campos_necesarios = ["Keywords", "Titulo", "Articulo", "Descripcion", "Categorias", "SLUG", "Portada", "Alt"]
        campos_faltantes = [campo for campo in campos_necesarios if campo not in encabezados]
        
        # Leer todas las filas
        for fila in lector:
            filas_originales.append(fila)
    
    # Si faltan campos, agregar los campos faltantes
    if campos_faltantes:
        print(f"Corrigiendo archivo {archivo_redactados}. Agregando campos faltantes: {campos_faltantes}")
        
        # Crear nuevos encabezados con los campos faltantes
        nuevos_encabezados = encabezados + campos_faltantes
        
        # Reescribir el archivo con los nuevos encabezados
        with open(archivo_redactados, "w", newline="", encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerow(nuevos_encabezados)
            
            # Escribir todas las filas, agregando valores vacíos para los campos nuevos
            for fila in filas_originales:
                nueva_fila = fila + [""] * len(campos_faltantes)
                escritor.writerow(nueva_fila)
        
        print(f"Archivo {archivo_redactados} corregido.")

print("\nProceso de limpieza finalizado correctamente.")
print("Ahora puedes ejecutar _0.Prompts.py para continuar el procesamiento desde donde se quedó.")
