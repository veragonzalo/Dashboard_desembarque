# 🐟 Dashboard Desembarque Pesquero — Chile 2000–2024

> Dashboard interactivo de análisis de desembarque pesquero en Chile, construido con Dash 4 + Plotly 6 y desplegado en producción con Render.

---

## 📋 Descripción

**Dashboard Desembarque Pesquero** es una aplicación web de análisis de datos que visualiza los registros históricos de desembarque pesquero en Chile entre los años 2000 y 2024. Permite explorar toneladas desembarcadas por especie, región, tipo de agente, tipo de aguas y distribución geográfica por puerto, con filtros dinámicos e interactivos.

Los datos se procesan con Pandas a partir de un archivo CSV (`BD_desembarque.csv`) con codificación `latin-1`, y los gráficos son servidos desde caché para optimizar tiempos de respuesta con filtros repetidos.

---

## 🚀 Características principales

- 📊 **Timeline por tipo de agente** — evolución anual del desembarque (Artesanal, Industrial, Acuicultura, Fábrica) con área rellena
- 🗺️ **Mapa geográfico de Chile** — 54 puertos georeferenciados con burbujas proporcionales al volumen desembarcado
- 🌲 **Treemap Top 30 especies** — distribución visual por volumen de las principales especies
- 📈 **Top 10 especies** — barras horizontales con las especies de mayor tonelaje
- 🍩 **Donut por tipo de agente** — participación porcentual de cada sector productivo
- 📍 **Barras por región** — toneladas acumuladas por región a lo largo del período
- 🃏 **KPIs en tiempo real** — toneladas totales, especie principal, puertos activos y período seleccionado
- 🌙 **Modo oscuro / modo claro** — toggle de tema con estilos adaptativos en todos los gráficos
- 🔍 **Filtros globales** — rango de años, región (multi-select), tipo de agente (checklist), tipo de aguas (nacionales / internacionales)
- ↺ **Resetear filtros** — botón para volver al estado inicial con un clic
- ⚡ **Caché de resultados** — `flask-caching` almacena los 6 gráficos por combinación de filtros durante 5 minutos

---

## 🗂️ Estructura del proyecto

```
Dashboard_desembarque/
│
├── csv/
│   └── BD_desembarque.csv      # Dataset principal (2000–2024, codificación latin-1)
│
├── assets/                     # Estilos CSS personalizados (dark/light mode, sidebar, cards)
│
├── dashboard.py                # Aplicación Dash completa (832 líneas)
│   ├── Sección 1: Carga y limpieza de datos con Pandas
│   ├── Sección 2: Coordenadas geográficas de 54 puertos
│   ├── Sección 3: Definición de temas dark / light
│   ├── Sección 4: Helpers de layout Plotly
│   ├── Sección 5: Funciones de gráficos (6 charts + KPIs)
│   ├── Sección 6: Layout de la app (sidebar + contenido principal)
│   ├── Sección 7: Callbacks (tema, filtros, dashboard principal)
│   └── Sección 8: Entry point (Gunicorn / local)
│
├── render.yaml                 # Configuración de despliegue en Render
├── requirements.txt            # Dependencias del proyecto
├── .python-version             # Versión de Python fijada
└── .gitignore
```

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| **Python** | — | Lenguaje principal |
| **Dash** | 4.0.0 | Framework de dashboards interactivos |
| **Plotly** | 6.6.0 | Gráficos: scatter, treemap, bar, pie, scattermap |
| **Dash Bootstrap Components** | 2.0.4 | Layout responsivo y componentes UI |
| **Pandas** | 3.0.1 | Carga, limpieza y agregación de datos CSV |
| **NumPy** | 2.4.3 | Cálculo de tamaño de burbujas en mapa |
| **Flask-Caching** | ≥2.0.0 | Caché en memoria de gráficos calculados |
| **Gunicorn** | 25.1.0 | Servidor WSGI para producción |
| **Render** | — | Hosting y despliegue en producción |

---

## 🌐 Demo en producción

El dashboard está disponible en:

👉 **[https://dashboard-desembarque.onrender.com](https://dashboard-desembarque.onrender.com/)**

> La primera carga puede tardar hasta 60 segundos si la app estuvo inactiva (plan gratuito de Render).

---

## ▶️ Cómo ejecutar el proyecto en local

### 1. Clonar el repositorio

```bash
git clone https://github.com/veragonzalo/Dashboard_desembarque.git
cd Dashboard_desembarque
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python dashboard.py
```

Abrir en: `http://localhost:8050/`

---

## 📊 Gráficos y visualizaciones

| Gráfico | Tipo | Descripción |
|---|---|---|
| Timeline | `go.Scatter` + área | Evolución anual por tipo de agente |
| Mapa de puertos | `go.Scattermap` | 54 puertos georeferenciados en Chile |
| Treemap especies | `px.treemap` | Top 30 especies por toneladas |
| Top 10 especies | `go.Bar` horizontal | Ranking de especies por volumen |
| Donut tipo agente | `go.Pie` | Participación porcentual por sector |
| Barras por región | `go.Bar` horizontal | Toneladas acumuladas por región |

---

## 🗃️ Datos

El dataset `BD_desembarque.csv` contiene registros de desembarque pesquero con las siguientes dimensiones:

| Columna | Descripción |
|---|---|
| `ano` | Año del registro (2000–2024) |
| `mes` | Mes del registro |
| `region` | Región de Chile |
| `puerto_desembarque` | Puerto donde se realizó el desembarque |
| `especie` | Especie desembarcada |
| `tipo_agente` | Sector: Artesanal, Industrial, Acuicultura, Fábrica |
| `aguas` | Tipo de aguas: NAC (nacionales) o AI (internacionales) |
| `toneladas` | Volumen desembarcado en toneladas métricas |

---

## 👩‍💻 Autora

**Vera Gonzalo** — [@veragonzalo](https://github.com/veragonzalo)

---

## 📚 Contexto académico

Proyecto desarrollado como parte del **Bootcamp Desarrollo de Aplicaciones Full Stack Python** — aplicando análisis de datos, visualización interactiva con Dash/Plotly y despliegue en producción con Render.

---

## 📄 Licencia

Este proyecto es de uso académico y educativo.
