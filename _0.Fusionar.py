import pandas as pd
import glob

archivos_csv = glob.glob('_0.CSVs/*.csv')
dataframes = [pd.read_csv(archivo) for archivo in archivos_csv]
df_combinado = pd.concat(dataframes, ignore_index=True)
df_subset = df_combinado[["Keywords", "Position", "Ranking Url"]]
df_subset = df_subset.sort_values(by="Position", ascending=True)
df_subset.to_csv('0. Fusionados.csv', index=False)
