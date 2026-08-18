# Cloud Data Geolocation (CDGeB) — Multi-Tier Services

Solución y pipeline de análisis para el desafío de Kaggle **[Cloud Data Geolocation 1 - Multi-Tier Services](https://www.kaggle.com/competitions/cloud-data-geolocation-1-multi-tier-services)**.

El objetivo del benchmark es determinar la región geográfica física (regiones de AWS) de 17 archivos de datos almacenados en buckets de Amazon S3 a partir de mediciones de latencia de red (RTT).

---

## 🏛️ Arquitectura del Sistema (3-Tier Model)

El sistema modela una arquitectura cliente-servidor-almacenamiento distribuida:

```
[ 14 GCP Probes ]  =======>  [ 17 AWS EC2 Front Servers ]  =======>  [ 17 AWS S3 Buckets ]
 Ubicación CONOCIDA              Ubicación CONOCIDA                  Ubicación OBJETIVO
```

- **Probes (GCP):** 14 clientes distribuidos globalmente (coordenadas geográficas conocidas).
- **Front-End Servers (AWS EC2):** 17 servidores de aplicación en 17 regiones de AWS (`AWS-01` a `AWS-17`, coordenadas conocidas).
- **Data Files (AWS S3):** 17 archivos (`cdgeb-file-01` a `17`) en buckets S3 en las 17 regiones (ubicación desconocida a predecir).

---

## ⚙️ Metodología y Pipeline

El tiempo total medido en cada petición HTTP corresponde a:

5127\text{RTT}_{\text{total}} \approx t_{\text{Probe} \leftrightarrow \text{Server}} + t_{\text{Server} \leftrightarrow \text{S3}} + t_{\text{overhead}}5127

### 1. Preprocesamiento y Filtrado de Ruido
- **Cold Start Filtering:** Se descarta `RTT1` debido a la penalización por resolución DNS, handshake TCP/TLS e inicialización de buffers.
- **Métrica Robusta:** Se calcula la **mediana** de las mediciones estables (`RTT2` a `RTT20`).

### 2. Descomposición del Tramo Conocido (Probe $\to$ Server)
- Cálculo de distancias geodésicas en kilómetros utilizando la **fórmula de Haversine**:
  5127d = 2r \arcsin \left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)5127
- Estimación del tiempo de propagación ida y vuelta por fibra óptica ( \approx 200{,}000\text{ km/s}$):
  5127t_{\text{Probe}\leftrightarrow\text{Server}} = \frac{2 \cdot d}{200{,}000\text{ km/s}}5127
- Aislamiento del tiempo residual hacia la capa de almacenamiento:
  5127\Delta t_{\text{Server}\leftrightarrow\text{S3}} = \text{RTT}_{\text{mediana}} - t_{\text{Probe}\leftrightarrow\text{Server}}5127

### 3. Estrategias de Resolución
- **Challenge-1 (Archivos 01 a 05):** Para cada archivo, uno de los 8 servidores evaluados se encuentra en la misma región que el bucket S3. Se identifica el servidor con $\Delta t$ mínimo (latencia intra-datacenter $\approx 0\text{ ms}$).
- **Challenge-2 (Archivos 06 a 17):** Ningún servidor evaluado comparte región con el archivo. Se realiza una triangulación / optimización de distancias minimizando el error residual cuadrático frente a la matriz de distancias inter-región de AWS.

---

## 📁 Estructura del Repositorio

```text
├── Measurements.csv       # Dataset de mediciones RTT (Probes -> Servers -> Files)
├── Probe_ID.txt           # Coordenadas geográficas de los 14 Probes de GCP
├── Server_ID.txt          # Coordenadas geográficas de los 17 Servidores de AWS EC2
├── Region_name.txt        # Mapeo de nombres e identificadores de región de AWS
├── solution_ch1.py        # Script de procesamiento y predicción para Challenge-1
└── submission_ch1.csv     # Formato de predicción final listo para submit
```

---

## 🚀 Requisitos y Ejecución

```bash
# Dependencias necesarias
pip install pandas numpy

# Ejecutar script de procesamiento
python solution_ch1.py
```
