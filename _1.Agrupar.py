import pandas as pd
import unicodedata

def contar_keywords(url, df_agrupado):
    serie = df_agrupado.loc[df_agrupado['Ranking Url'] == url, 'Keywords'].str.count('\n')
    return serie.values[0] if not serie.empty else 0

df = pd.read_csv('0. Fusionados.csv', encoding='utf-8')
df['Keywords'] = df['Keywords'].fillna('')
df['Keywords'] = df['Keywords'].apply(lambda x: unicodedata.normalize('NFKD', x))

df_agrupado = df.groupby('Ranking Url', as_index=False).agg({'Keywords': '\n'.join})
df_agrupado = df_agrupado[['Keywords', 'Ranking Url']]

keyword_compartidas = {}
for index, fila in df_agrupado.iterrows():
    for keyword in fila['Keywords'].split('\n'):
        if keyword:
            keyword_compartidas.setdefault(keyword, []).append(fila['Ranking Url'])

urls_a_eliminar = set()
for keyword, urls in keyword_compartidas.items():
    if len(urls) > 1:
        url_maxima = max(urls, key=lambda u: contar_keywords(u, df_agrupado))
        df_subset = df_agrupado[df_agrupado['Ranking Url'].isin(urls)]
        keywords_unidas = '\n'.join(df_subset['Keywords'].values)
        keywords_lista = keywords_unidas.split('\n')
        keyword_combinadas = '\n'.join(set(keywords_lista))
        df_agrupado.loc[df_agrupado['Ranking Url'] == url_maxima, 'Keywords'] = keyword_combinadas
        urls_a_eliminar.update(u for u in urls if u != url_maxima)

# Eliminación de las URLs marcadas, barajado de las filas y guardado del archivo resultante
df_agrupado = df_agrupado[~df_agrupado['Ranking Url'].isin(urls_a_eliminar)]
df_agrupado = df_agrupado.sample(frac=1).reset_index(drop=True)
df_agrupado.to_csv('1. Agrupados.csv', index=False, encoding='utf-8')
