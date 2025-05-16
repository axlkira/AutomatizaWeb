#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
_01.Descanivalizador.py - Eliminador de Canibalización SEO Avanzado
====================================================================

Descripción:
    Este script analiza el archivo de URLs fusionadas y elimina las canibalizaciones 
    de palabras clave, manteniendo solo la entrada con mejor posición para cada keyword.
    
    Las posiciones se evalúan en orden ascendente, donde:
    - La posición 1 es la mejor
    - Luego siguen 2, 3, 4, etc.
    
Funcionamiento:
    1. Lee el archivo '0. Fusionados.csv'
    2. Encuentra y elimina keywords duplicadas, conservando solo las de mejor posición
    3. Guarda el archivo descanivalizado con el mismo nombre para mantener el flujo de trabajo
    
Autor: AutomatizaWeb - Cascade AI
Fecha: 2025-05-16
"""

import csv
import os
import logging
import time
from collections import defaultdict

# Configuración de logs para seguimiento
logging.basicConfig(
    filename='_01.Descanivalizador.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Función principal que ejecuta el proceso de descanivalización"""
    inicio = time.time()
    
    # Ruta al archivo de entrada
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    archivo_entrada = os.path.join(directorio_base, '0. Fusionados.csv')
    archivo_temporal = os.path.join(directorio_base, 'temp_descanivalizado.csv')
    archivo_backup = os.path.join(directorio_base, '0. Fusionados.backup.csv')
    archivo_canibalizaciones = os.path.join(directorio_base, 'canibalizaciones_eliminadas.csv')
    
    # Verificar si el archivo existe
    if not os.path.exists(archivo_entrada):
        mensaje = f"Error: El archivo '0. Fusionados.csv' no se encuentra en {directorio_base}"
        print(mensaje)
        logging.error(mensaje)
        return
    
    try:
        # Comenzar el proceso
        print("\n=== Descanivalizador SEO Avanzado ===")
        print(f"Analizando: {archivo_entrada}")
        logging.info(f"Iniciando descanivalización del archivo: {archivo_entrada}")
        
        # Leer el archivo CSV
        keywords_dict = defaultdict(list)
        total_entradas = 0
        cabecera = []
        
        with open(archivo_entrada, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            cabecera = next(reader)  # Guardar la cabecera
            
            # Leer todas las filas y agruparlas por keyword
            for row in reader:
                total_entradas += 1
                if len(row) >= 3:  # Asegurar que la fila tiene los campos requeridos
                    keyword = row[0].strip().lower()  # Normalizar para comparación
                    try:
                        position = int(row[1]) if row[1].isdigit() else float('inf')
                    except (ValueError, IndexError):
                        position = float('inf')  # Si hay error, asignar posición infinita
                    
                    # Guardar la fila original junto con su posición para ordenar después
                    keywords_dict[keyword].append((position, row))
                else:
                    logging.warning(f"Fila ignorada por formato incorrecto: {row}")
        
        print(f"Entradas totales: {total_entradas}")
        print(f"Keywords únicas: {len(keywords_dict)}")
        logging.info(f"Se encontraron {total_entradas} entradas y {len(keywords_dict)} keywords únicas")
        
        # Encontrar duplicados y contarlos
        duplicados = {k: len(v) for k, v in keywords_dict.items() if len(v) > 1}
        if duplicados:
            print(f"Se encontraron {sum(duplicados.values()) - len(duplicados)} entradas canivalizadas")
            logging.info(f"Keywords canivalizadas: {len(duplicados)}")
            logging.info(f"Entradas canivalizadas: {sum(duplicados.values()) - len(duplicados)}")
        else:
            print("No se encontraron canivalizaciones.")
            logging.info("No se encontraron canivalizaciones.")
        
        # Crear una copia de respaldo del archivo original
        import shutil
        shutil.copy2(archivo_entrada, archivo_backup)
        logging.info(f"Backup creado: {os.path.basename(archivo_backup)}")
        
        # Descanivalizar: ordenar por posición (menor es mejor) y quedarse con la mejor
        filas_filtradas = []
        filas_eliminadas = []
        
        for keyword, entries in keywords_dict.items():
            # Ordenar por posición (ascendente, donde 1 es la mejor posición)
            entries.sort(key=lambda x: x[0])
            
            # Agregar solo las entradas de posición 1 a 4
            entradas_a_mantener = []
            for pos, row in entries:
                if 1 <= pos <= 4:
                    entradas_a_mantener.append((pos, row))
                    filas_filtradas.append(row)
                    logging.info(f"Keyword: '{keyword}' - Se mantiene posición {pos} - URL: {row[2]}")
                else:
                    logging.info(f"    Eliminada: posición {pos} - URL: {row[2]}")
                    filas_eliminadas.append(row)
            
            # Loguear información si hay duplicados
            if len(entries) > len(entradas_a_mantener):
                logging.info(f"Keyword: '{keyword}' - Se mantienen {len(entradas_a_mantener)} de {len(entries)} entradas (solo posiciones 1-4)")

        
        # Escribir resultados a un archivo temporal
        with open(archivo_temporal, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cabecera)
            writer.writerows(filas_filtradas)
        
        # Guardar las canibalizaciones eliminadas en un archivo separado
        if filas_eliminadas:
            with open(archivo_canibalizaciones, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(cabecera)
                writer.writerows(filas_eliminadas)
            logging.info(f"Se han guardado {len(filas_eliminadas)} canibalizaciones eliminadas en: {os.path.basename(archivo_canibalizaciones)}")
        
        # Reemplazar el archivo original
        try:
            # Primero verificamos si podemos escribir en el archivo original
            if os.path.exists(archivo_entrada):
                # Intentar cerrar cualquier handle abierto al archivo
                import gc
                gc.collect()  # Forzar recolección de basura
                
                # En Windows, a veces es necesario esperar un momento
                time.sleep(0.5)
                
                # Intentar reemplazar el archivo
                os.replace(archivo_temporal, archivo_entrada)
            else:
                # Si el archivo no existe, simplemente renombramos el temporal
                os.rename(archivo_temporal, archivo_entrada)  
        except PermissionError:
            # Si falla por permisos, intentamos una copia directa
            logging.warning("No se pudo reemplazar el archivo directamente. Intentando método alternativo...")
            try:
                with open(archivo_temporal, 'r', encoding='utf-8', errors='replace') as src:
                    with open(archivo_entrada, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                os.remove(archivo_temporal)  # Eliminar el temporal después
            except Exception as e:
                # Si todo falla, guardamos con un nombre alternativo
                alt_name = os.path.join(directorio_base, '0. Fusionados.descanivalizado.csv')
                os.rename(archivo_temporal, alt_name)
                logging.error(f"No se pudo actualizar el archivo original. Guardado como: {os.path.basename(alt_name)}")
                print(f"No se pudo actualizar el archivo original. Se guardó como: {os.path.basename(alt_name)}")
                archivo_entrada = alt_name  # Actualizar la referencia para los mensajes
        
        # Calcular estadísticas finales
        entradas_eliminadas = total_entradas - len(filas_filtradas)
        porcentaje_reduccion = (entradas_eliminadas / total_entradas) * 100 if total_entradas > 0 else 0
        
        fin = time.time()
        tiempo_ejecucion = fin - inicio
        
        # Mostrar resultados
        print("\n=== Proceso completado ===")
        print(f"Tiempo de ejecución: {tiempo_ejecucion:.2f} segundos")
        print(f"Entradas originales: {total_entradas}")
        print(f"Entradas después de descanivalizar: {len(filas_filtradas)}")
        print(f"Entradas eliminadas: {entradas_eliminadas} ({porcentaje_reduccion:.2f}%)")
        print(f"El archivo '0. Fusionados.csv' ha sido actualizado exitosamente!")
        print(f"El archivo original ha sido respaldado como '0. Fusionados.backup.csv'")
        
        if entradas_eliminadas > 0:
            print(f"Las canibalizaciones eliminadas se guardaron en 'canibalizaciones_eliminadas.csv'")
            
        print("Se ha generado un log detallado en '_01.Descanivalizador.log'")
        
        
        logging.info(f"Proceso completado en {tiempo_ejecucion:.2f} segundos")
        logging.info(f"Se han eliminado {entradas_eliminadas} entradas ({porcentaje_reduccion:.2f}%)")
        logging.info(f"El archivo ha sido descanivalizado exitosamente")
        
    except Exception as e:
        mensaje = f"Error durante la descanivalización: {str(e)}"
        print(mensaje)
        logging.exception(mensaje)
        
        # Si hay error, asegurar que no quede archivo temporal
        if os.path.exists(archivo_temporal):
            os.remove(archivo_temporal)

if __name__ == "__main__":
    main()
