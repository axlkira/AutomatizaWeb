# Proyecto: Automatización de Generación de Contenido Web SEO

## Descripción
Este proyecto automatiza el proceso de scraping, categorización, agrupación, redacción y optimización SEO de contenido web. Utiliza modelos de lenguaje avanzados (como Ollama local o OpenAI) para generar resúmenes, títulos, artículos, descripciones y categorías a partir de datos extraídos de la web.

## Estructura del Proyecto

```
Metodo_monetiza_ya/
├── _0.CSVs/                  # Archivos CSV de entrada
├── _0.Fusionar.py            # Fusiona múltiples CSV en uno solo
├── _1.Agrupar.py             # Agrupa y filtra datos fusionados
├── _2.Escrapear.py           # Extrae artículos y metadatos de URLs
├── _3.Categorizar.py         # Clasifica y categoriza los títulos usando IA
├── _4.Redactar.py            # Genera resúmenes, títulos, artículos y descripciones SEO
├── _1.Prompts/               # Prompts en formato JSON para cada tarea
│   ├── 0.Categorias.json
│   ├── 1.Resumen.json
│   ├── 2.Titulo.json
│   ├── 3.Articulo.json
│   ├── 4.Descripcion.json
│   └── 5.Categoria.json
├── 0. Fusionados.csv         # CSV fusionado
├── 1. Agrupados.csv          # CSV agrupado
├── 2. Scrapeados.csv         # Datos scrapeados
├── 3. Categorias.txt         # Categorías generadas
├── 4. Redactados.csv         # Artículos redactados
└── README.md                 # Documentación
```

## Requisitos
- Python 3.8+
- Paquetes: `requests`, `pandas`, `beautifulsoup4`, `newspaper3k`, `markdown2`, `tqdm`, `openai` (opcional)
- **Ollama** instalado localmente (para modelos como `qwen3:8b`) o clave de API de OpenAI si usas la nube.

Instala dependencias con:
```bash
pip install requests pandas beautifulsoup4 newspaper3k markdown2 tqdm openai
```

## Uso de la función universal `chat`

La función `chat` permite alternar entre distintos proveedores de modelos de lenguaje (Ollama local, OpenAI, etc.) sin cambiar la lógica del pipeline. Por defecto, usa Ollama local con el modelo `qwen3:8b`.

### Ejemplo de uso
```python
# Uso por defecto (Ollama local):
respuesta = chat(prompt, reemplazos)

# Para usar OpenAI (requiere instalar openai y tener API key):
respuesta = chat(prompt, reemplazos, api_type='openai', api_config={'api_key': 'TU_API_KEY', 'model': 'gpt-3.5-turbo'})
```

### Parámetros de la función
- `pjson`: Prompt en formato lista de mensajes (como espera OpenAI/Ollama).
- `reemplazos`: Diccionario de reemplazos para variables en el prompt.
- `api_type`: `'ollama'` (por defecto) o `'openai'`.
- `api_config`: Diccionario con configuración específica (modelo, base_url, api_key).

### Ventajas
- **Flexible:** Puedes cambiar de proveedor de IA fácilmente.
- **Centralizado:** Toda la lógica de conexión está en una sola función.
- **Compatible:** No rompe el funcionamiento actual; solo cambia si lo necesitas.

## Pipeline de uso típico
1. **Coloca tus CSV de palabras clave en `_0.CSVs/`.**
2. Ejecuta los scripts en orden:
    1. `_0.Fusionar.py`
    2. `_1.Agrupar.py`
    3. `_2.Escrapear.py`
    4. `_3.Categorizar.py`
    5. `_4.Redactar.py`
3. Obtén tus resultados en los archivos generados (`4. Redactados.csv`, etc.)

## Explicación técnica de la función universal
La función `chat` detecta el tipo de API (Ollama u OpenAI) y realiza la petición adecuada:
- Para **Ollama**: Hace una petición HTTP local al endpoint `/chat/completions`.
- Para **OpenAI**: Usa el SDK oficial y tu clave de API.
- Puedes expandir a otros proveedores agregando más ramas en la función.

## Notas y recomendaciones
- Si usas Ollama, asegúrate de que el modelo esté descargado y corriendo (`ollama serve`).
- Si usas OpenAI, necesitas una clave válida y conexión a internet.
- Los prompts deben estar en formato compatible con chat (lista de diccionarios).
- Puedes personalizar los modelos y endpoints en el parámetro `api_config`.

## Créditos y soporte
Desarrollado para automatizar la generación de contenido SEO usando IA local o en la nube. Si tienes dudas, revisa el código fuente y la función `chat` universal para adaptarlo a tus necesidades.

---

**Resumen de la explicación dada:**
- El sistema ahora es universal y flexible: puedes alternar entre IA local (Ollama) y la nube (OpenAI) sin romper el flujo.
- La lógica y esencia original del proyecto se mantiene intacta.
- Puedes ampliar el soporte a más proveedores fácilmente.
