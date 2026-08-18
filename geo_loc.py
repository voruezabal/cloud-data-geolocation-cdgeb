#%%
import pandas as pd 
import numpy as np
#%%
PATH_DATA = "/home/victoria/Documents/Kaggle_proj/Measurements.csv"

df = pd.read_csv(PATH_DATA)

PATH_COORD = "/home/victoria/Documents/Kaggle_proj/Region_name.txt"

df_coord = pd.read_csv(PATH_COORD, sep=r"\s\s+", header = 0)

PATH_SERVER = "/home/victoria/Documents/Kaggle_proj/Server_ID.txt"
df_server = pd.read_csv(PATH_SERVER, sep=r"\s\s+", header = 0)

PATH_PROBE = "/home/victoria/Documents/Kaggle_proj/Probe_ID.txt"
df_probe = pd.read_csv(PATH_PROBE, sep=r"\s\s+", header = 0)

#%%
df = df[df["Difficulty"] == "Challenge-1"]
print(df)
#%% Filter Rtt1 as it takes into consideration de cold start

df = df.drop(columns = "RTT1") 
#%% Median of the column

median = df.median(axis = 1 , numeric_only = True)

#%%
# Filter out specific columns into a new DataFrame
df_latency = df.filter(['Probe', 'Front Server', 'Data File' ])

df_latency['latency'] = median
#%%

def haversine_formula(lat1, lon1, lat2, lon2):
    import math
    r = 6372.8
    dlat = math.radians(lat2 - lat1 )
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = math.sin(dlat / 2) **2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(a**(1/2))

    dist = r*c
    return dist
# %%
dist = np.zeros((len(df_server),len(df_probe)))
for i in range(len(df_server)):
    for j in range(len(df_probe)):
        dist[i,j] = haversine_formula(df_server["Lat."].iloc[i], df_server["Long."].iloc[i],
                                      df_probe["Lat."].iloc[j], df_probe["Long."].iloc[j])

#%% 
travel_time= dist*2 / 200_000
# %%
df_travel = pd.DataFrame(
    travel_time, 
    index=df_server['Server ID'],  # Reemplaza por la columna real de IDs en df_server
    columns=df_probe['Probe ID']   # Reemplaza por la columna real de IDs en df_probe
)

# 2. Agregar el tiempo de viaje a df_latency
# Se usa zip() para buscar la intersección (Server, Probe) directamente
df_latency['travel_time'] = [
    df_travel.loc[server, probe] 
    for server, probe in zip(df_latency['Front Server'], df_latency['Probe'])
]
# %%

df_latency["time3"] = df_latency["latency"] - df_latency["travel_time"]
# %%
# 1. Agrupar por Archivo y Servidor tomando la mediana del tiempo restante (time3)
server_file_latencies = df_latency.groupby(['Data File', 'Front Server'])['time3'].median().reset_index()

# 2. Para cada archivo, encontrar el Front Server con el menor time3
best_servers = server_file_latencies.loc[
    server_file_latencies.groupby('Data File')['time3'].idxmin()
]

# 3. Mapear cada Server ID a su región correspondiente (ej. uniendo con df_server)
# Si df_server tiene columnas ['Server ID', 'Region ID'] o similar:
results_ch1 = best_servers.merge(
    df_server[['Server ID', 'Region ID']], 
    left_on='Front Server', 
    right_on='Server ID', 
    how='left'
)[['Data File', 'Region ID']]

print(results_ch1)
# %%


# %%
# Unir contra df_coord (que tiene Region ID y Server ID)
results_ch1 = best_servers.merge(
    df_coord[['Server ID', 'Region Name']], 
    left_on='Front Server', 
    right_on='Server ID', 
    how='left'
)[['Data File', 'Region Name']]

print(results_ch1)
# %%
# 1. Asegurar los nombres de columna requeridos por Kaggle
submission_df = results_ch1.rename(columns={'Region ID': 'AWS region'})[['Data File', 'AWS region']]

# 2. Guardar en CSV sin el índice de pandas
OUTPUT_PATH = "/home/victoria/Documents/Kaggle_proj/submission_ch1.csv"
submission_df.to_csv(OUTPUT_PATH, index=False)

print(f"Archivo guardado exitosamente en: {OUTPUT_PATH}")