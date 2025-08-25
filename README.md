# PT_CALIDAD

Sistema de Control de Calidad basado en Streamlit, inspirado en la estructura del proyecto [alzaqr](https://github.com/Egem97/alzaqr).

## 🚀 Características

- **Dashboard Interactivo**: Panel de control con métricas en tiempo real
- **Control de Calidad**: Sistema completo de evaluaciones de productos
- **Reportes Avanzados**: Generación de reportes diarios, semanales y mensuales
- **Gestión de Usuarios**: Sistema de roles y permisos
- **Base de Datos SQLite**: Almacenamiento local de datos
- **Interfaz Moderna**: Diseño responsive con Streamlit

## 📁 Estructura del Proyecto

```
PT_CALIDAD/
├── app_streamlit.py          # Aplicación principal
├── styles.py                 # Estilos CSS personalizados
├── requirements.txt          # Dependencias del proyecto
├── Dockerfile               # Configuración Docker
├── docker-compose.yml       # Orquestación Docker
├── .gitignore              # Archivos a ignorar por Git
├── README.md               # Documentación
├── .streamlit/             # Configuración de Streamlit
│   └── config.toml
├── views/                  # Vistas de la aplicación
│   ├── __init__.py
│   ├── home.py            # Página de inicio
│   ├── quality_control.py # Control de calidad
│   ├── reports.py         # Reportes
│   └── settings.py        # Configuración
├── utils/                  # Utilidades
│   ├── __init__.py
│   └── config.py          # Gestión de configuración
├── src/                   # Código fuente principal
│   ├── __init__.py
│   └── database.py        # Gestión de base de datos
└── data/                  # Datos de la aplicación
    └── pt_calidad.db      # Base de datos SQLite
```

## 🛠️ Configuración del Entorno de Desarrollo

### 1. Crear entorno virtual
```bash
python -m venv venv
```

### 2. Activar entorno virtual
#### Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt):
```cmd
venv\Scripts\activate.bat
```

#### Linux/macOS:
```bash
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
streamlit run app_streamlit.py
```

## 🐳 Ejecución con Docker

### Usando Docker Compose (Recomendado)
```bash
docker-compose up -d
```

### Usando Docker directamente
```bash
# Construir imagen
docker build -t pt-calidad .

# Ejecutar contenedor
docker run -p 8501:8501 pt-calidad
```

## 📊 Funcionalidades Principales

### 🏠 Dashboard
- Métricas en tiempo real
- Gráficos de tendencias
- Actividades recientes
- Información del sistema

### 📊 Control de Calidad
- **Nueva Evaluación**: Formulario completo para evaluar productos
- **Historial**: Consulta de evaluaciones anteriores
- **Análisis**: Gráficos y estadísticas de calidad
- **Criterios**: Configuración de estándares de calidad

### 📈 Reportes
- **Dashboard**: Vista general de métricas
- **Reporte Diario**: Análisis detallado por día
- **Reporte Semanal**: Tendencias semanales
- **Reporte Mensual**: Resumen mensual completo

### ⚙️ Configuración
- **General**: Configuración de la empresa y sistema
- **Usuarios**: Gestión de usuarios y roles
- **Criterios**: Configuración de estándares de calidad
- **Base de Datos**: Configuración y respaldos

## 🗄️ Base de Datos

El sistema utiliza SQLite con las siguientes tablas principales:

- **evaluations**: Registro de evaluaciones de calidad
- **users**: Gestión de usuarios del sistema
- **quality_criteria**: Criterios de evaluación
- **system_config**: Configuración del sistema

## 🎨 Personalización

### Estilos CSS
Los estilos se pueden personalizar editando el archivo `styles.py`.

### Configuración
La configuración del sistema se maneja a través de `utils/config.py` y se almacena en `config.json`.

## 🔧 Comandos Útiles

- **Activar entorno**: `.\venv\Scripts\Activate.ps1`
- **Desactivar entorno**: `deactivate`
- **Instalar paquete**: `pip install nombre_paquete`
- **Guardar dependencias**: `pip freeze > requirements.txt`
- **Ejecutar tests**: `pytest`
- **Formatear código**: `black .`
- **Verificar estilo**: `flake8`

## 🌐 Acceso a la Aplicación

Una vez ejecutada, la aplicación estará disponible en:
- **Local**: http://localhost:8501
- **Docker**: http://localhost:8501

## 📝 Notas de Desarrollo

- El proyecto está basado en la estructura del repositorio [alzaqr](https://github.com/Egem97/alzaqr)
- Utiliza Streamlit para la interfaz de usuario
- Implementa una arquitectura modular con separación de vistas, utilidades y lógica de negocio
- Incluye sistema de configuración flexible
- Soporte completo para Docker y Docker Compose

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
