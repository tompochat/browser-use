# Agente de Automatización Web con Gemini y Streamlit

Este proyecto permite automatizar tareas web usando un agente controlado por IA (Gemini) y una interfaz visual simple con Streamlit.

## Requisitos previos

- **Python 3.10 o superior**
- **Git**
- Acceso a una cuenta de Google Cloud para obtener el archivo de credenciales (service account JSON)
- Clave de API de Gemini (opcional, según integración)

## Instalación paso a paso

### 1. Instalar Python
- Descarga Python desde [python.org](https://www.python.org/downloads/)
- Durante la instalación, marca la opción "Add Python to PATH"

### 2. Clonar el repositorio
```sh
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
```

### 3. Crear y activar un entorno virtual
```sh
python -m venv env_ia
# En Windows:
env_ia\Scripts\activate
# En Mac/Linux:
source env_ia/bin/activate
```

### 4. Instalar dependencias
```sh
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto (puedes copiar y editar el ejemplo de abajo):

```
GEMINI_API_KEY=tu_api_key_opcional
GOOGLE_APPLICATION_CREDENTIALS=C:\ruta\a\tu\clave.json
USERNAME=tu_usuario
PASSWORD=tu_password
YOIZEN_URL=https://qa.ysocial.net/Test/Login.aspx
```

- **GOOGLE_APPLICATION_CREDENTIALS**: Debe ser la ruta absoluta al archivo JSON de tu cuenta de servicio de Google Cloud. [Guía oficial](https://cloud.google.com/docs/authentication/getting-started)
- **NO subas tu archivo `.env` ni el JSON de credenciales a ningún repositorio público.**

### 6. Ejecutar la aplicación

#### Opción 1: Interfaz visual (recomendada)
```sh
streamlit run app.py
```

#### Opción 2: Por consola
```sh
python main.py "Tu tarea aquí"
```

## Notas
- El archivo `.env` y el JSON de credenciales están en `.gitignore` y **no se suben al repositorio**.
- Si tienes problemas con dependencias, asegúrate de estar en el entorno virtual y de tener Python actualizado.
- Para más detalles sobre la clave de Google Cloud, consulta la [documentación oficial](https://cloud.google.com/docs/authentication/getting-started).

## Estructura del proyecto
- `main.py`: Lógica principal del agente.
- `app.py`: Interfaz visual con Streamlit.
- `site_navigation.py`: Mapeo de navegación para el agente.
- `.env`: Variables de entorno (no se sube al repo).
- `env_ia/`: Entorno virtual (no se sube al repo).

---

**¡Listo! Ahora puedes usar tu agente de automatización web con Gemini.**
