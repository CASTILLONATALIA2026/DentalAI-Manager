# 🦷 DentalAI Manager

Aplicación de gestión clínica dental desarrollada en **Python**, con interfaz gráfica en **CustomTkinter**, persistencia de datos mediante **SQLite**, generación de documentación y una **API REST desarrollada con FastAPI**.

DentalAI Manager es un proyecto de portfolio en desarrollo activo, creado para aplicar programación y digitalización a un entorno sanitario. El objetivo es demostrar una solución funcional y modular mediante la integración de interfaz gráfica, bases de datos, automatización documental y herramientas de apoyo al análisis clínico.

> **Nota:** proyecto educativo y de portfolio. No sustituye software clínico certificado ni el diagnóstico o criterio de un profesional sanitario.

## ✨ Funcionalidades

### 👥 Gestión de pacientes
- Alta, edición y eliminación de pacientes
- Búsqueda y consulta de información
- Teléfono, email y observaciones
- Persistencia mediante SQLite
- Importación de datos desde JSON
- Exportación de datos a Excel
- Generación de informes PDF

### 💊 Prescripciones
- Creación de prescripciones asociadas a pacientes
- Registro de medicamento, dosis, frecuencia y duración
- Indicaciones para el paciente
- Historial y consulta detallada
- Gestión del estado de las prescripciones
- Persistencia mediante SQLite

### 🤖 Módulo de apoyo al análisis clínico
- Registro de síntomas y duración
- Nivel de dolor
- Antecedentes relevantes
- Registro de fiebre e inflamación
- Generación de valoración orientativa
- Priorización del caso
- Sugerencia de pruebas
- Identificación de señales de alarma
- Almacenamiento de los análisis realizados

> Los resultados generados por este módulo son orientativos y requieren siempre validación profesional.

### 📋 Historial de análisis
- Consulta de análisis realizados
- Búsqueda por paciente
- Filtrado por estado
- Estados Pendiente, Validado y Rechazado
- Vista detallada de cada análisis
- Exportación a PDF

### 📊 Dashboard y estadísticas
- Número de pacientes registrados
- Análisis pendientes, validados y rechazados
- Edad promedio
- Distribución entre pacientes menores y adultos
- Tratamiento más frecuente

### 📄 Documentación
- Informes asociados a pacientes
- Informes de análisis
- Generación de PDF
- Exportación de información a Excel

## 🌐 API REST con FastAPI

DentalAI Manager incluye `api.py`, una **API REST desarrollada con FastAPI** que reutiliza la capa de datos de la aplicación.

### Endpoints disponibles

| Método | Endpoint | Función |
| --- | --- | --- |
| `GET` | `/` | Comprobar el estado de la API |
| `GET` | `/patients` | Listar pacientes |
| `GET` | `/patients/{patient_id}` | Consultar un paciente |
| `POST` | `/patients` | Crear un paciente |
| `PUT` | `/patients/{patient_id}` | Actualizar un paciente |
| `DELETE` | `/patients/{patient_id}` | Eliminar un paciente |

FastAPI genera automáticamente documentación interactiva mediante OpenAPI:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## 🛠️ Tecnologías utilizadas

- **Python**
- **FastAPI** — API REST
- **Uvicorn** — servidor ASGI
- **SQLite** — persistencia de datos
- **CustomTkinter / Tkinter / ttk** — interfaz gráfica
- **OpenPyXL** — exportación a Excel
- **ReportLab** — generación de PDF
- **JSON** — importación de información
- **Git & GitHub** — control de versiones

## 📁 Estructura principal

```text
DentalAI-Manager/
├── app.py
├── api.py
├── database.py
├── copilot_logic.py
├── pdf_utils.py
├── requirements.txt
├── run.bat
├── README.md
└── screenshots/
```

### Archivos principales

- `app.py` — interfaz principal y coordinación de la aplicación.
- `api.py` — API REST desarrollada con FastAPI.
- `database.py` — persistencia y operaciones sobre SQLite.
- `copilot_logic.py` — lógica del módulo de apoyo al análisis.
- `pdf_utils.py` — generación de informes PDF.
- `requirements.txt` — dependencias necesarias para ejecutar el proyecto.

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/CASTILLONATALIA2026/DentalAI-Manager.git
cd DentalAI-Manager
```

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
python app.py
```

### 4. Ejecutar la API REST

```bash
uvicorn api:app --reload
```

Después puede abrirse Swagger UI en:

`http://127.0.0.1:8000/docs`

## 🖥️ Capturas de pantalla

### Dashboard
![Dashboard de DentalAI Manager](screenshots/dashboard.png)

### Gestión de pacientes
![Gestión de pacientes](screenshots/pacientes.png)

### Prescripciones
![Gestión de prescripciones](screenshots/prescripciones.png)

### Historial de IA
![Historial de análisis IA](screenshots/historial_ia.png)

### Detalle de análisis IA
![Detalle de análisis clínico](screenshots/detalle_ia.png)

> Todos los pacientes y datos mostrados en las capturas son **ficticios** y se utilizan exclusivamente con fines demostrativos.

## 🔒 Privacidad y datos

DentalAI Manager utiliza una base de datos **SQLite local**.

Los archivos de base de datos (`*.db`) están excluidos del control de versiones mediante `.gitignore` para evitar publicar información almacenada localmente.

El repositorio público no debe contener información clínica real. Los pacientes y datos utilizados para demostraciones y capturas son ficticios.

## ⚠️ Alcance del proyecto

DentalAI Manager es un proyecto desarrollado con fines educativos y de portfolio.

Las funcionalidades relacionadas con análisis clínico y prescripciones **no sustituyen el diagnóstico, criterio ni supervisión de un profesional sanitario**.

## 🗺️ Próximas mejoras

- Ampliación de funcionalidades de IA aplicada
- Sistema de autenticación y usuarios
- Mejora de validación y manejo de errores de la API
- Incorporación de pruebas automatizadas
- Mejora de estadísticas y visualizaciones
- Evolución progresiva de la arquitectura

## 🎯 Qué demuestra este proyecto

- Desarrollo de una aplicación funcional con Python
- Programación orientada a objetos
- Diseño de interfaces gráficas
- Modelado y persistencia con SQLite
- Operaciones CRUD
- Creación de una API REST con FastAPI
- Documentación automática con Swagger/OpenAPI
- Generación de PDF y exportación a Excel
- Organización modular del código
- Git y control de versiones
- Aplicación de tecnología a un problema del entorno sanitario

## 📌 Estado del proyecto

**Versión funcional en desarrollo activo.**
