import streamlit as st
import subprocess
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Agente Web con Gemini", layout="centered")
st.title("Agente de Automatización Web con Gemini")

# Paso 1: Ingreso de tarea inicial
tarea_inicial = st.text_area("Tarea Inicial", value=st.session_state.get("tarea_inicial", ""), key="tarea_inicial")

# Paso 2: Mejorar tarea con IA
tarea_mejorada = st.session_state.get("tarea_mejorada", "")
if st.button("Mejorar Tarea con IA"):
    if not tarea_inicial.strip():
        st.warning("Por favor, ingresa una tarea inicial.")
    else:
        with st.spinner("Mejorando tarea con Gemini..."):
            llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash')
            prompt = f"""
Eres un asistente experto en la creación de prompts para agentes de automatización web.
Tu objetivo es refinar la tarea del usuario para que sea una instrucción clara, detallada, paso a paso y sin ambigüedades para un agente de IA que navegará un sitio web y realizará acciones. El agente testeará funcionalidades.

Tarea original del usuario:
'{tarea_inicial}'

Instrucciones para refinar la tarea:
1.  **Navegación Clara:** Si la tarea implica ir a una sección específica del sitio (ej: "reporte de colas", "configuración de usuarios"), comienza el prompt con una frase de navegación concisa. Usa nombres canónicos si los conoces o son inferibles. Por ejemplo: "Ve al reporte de colas en tiempo real." o "Accede a la configuración de usuarios."
2.  **Acciones Detalladas:** Después de la instrucción de navegación (si aplica), describe las acciones específicas que el agente debe realizar en esa página o sección. Sé explícito sobre con qué elementos interactuar (botones, menús, campos de texto, grillas) y qué información buscar o verificar.
3.  **Identificadores:** Usa nombres exactos de menús, botones, etiquetas o secciones si la tarea original los provee o son estándar. Para elementos genéricos, proporciona criterios claros (ej: 'el primer botón azul', 'el campo de texto etiquetado "Nombre"', 'la fila de la grilla que contiene "Emergencia"').
4.  **Extracción de Información:** Si se debe extraer información, especifica qué datos y, si es posible, el formato esperado.
5.  **Concisión y Precisión:** El prompt final debe ser directo y no contener información superflua. Evita ambigüedades.

Considera que el agente ya sabrá cómo iniciar sesión. Tu prompt debe enfocarse en las acciones *después* del login.

Devuelve ÚNICAMENTE el prompt refinado, listo para ser usado por el agente. No incluyas saludos, explicaciones previas ni posteriores a tu respuesta.

Ejemplo de un buen prompt refinado para la tarea "quiero ver las colas y chequear soporte":
"Ve al reporte de colas en tiempo real. Luego, en la grilla de colas, busca la cola con el nombre 'Soporte Nivel 1' y verifica que el número de agentes conectados sea mayor a 0."
"""
            try:
                response = llm.invoke(prompt)
                tarea_mejorada = response.content if hasattr(response, 'content') else str(response)
                st.session_state["tarea_mejorada"] = tarea_mejorada.strip() # Añadir strip()
            except Exception as e:
                st.error(f"Error al mejorar la tarea: {e}")

# Paso 3: Revisión y edición de la tarea mejorada
if tarea_mejorada:
    tarea_mejorada = st.text_area("Tarea Mejorada (puedes editarla antes de ejecutar)", value=tarea_mejorada, key="tarea_mejorada_editable")
    st.session_state["tarea_mejorada"] = tarea_mejorada

# Paso 4: Ejecutar agente con la tarea mejorada
if st.button("Ejecutar Agente con esta Tarea"):
    if not tarea_mejorada.strip():
        st.warning("No hay tarea mejorada para ejecutar.")
    else:
        with st.spinner("Ejecutando agente..."):
            try:
                # Usar sys.executable para asegurar el intérprete correcto
                process = subprocess.run(
                    [sys.executable, "main.py", tarea_mejorada],
                    capture_output=True,
                    text=True,
                    check=False
                )
                st.subheader("Resultado del Agente:")
                if process.stdout:
                    st.code(process.stdout)
                if process.stderr:
                    st.error(f"Errores durante la ejecución:\n{process.stderr}")
            except Exception as e:
                st.error(f"Error al ejecutar el agente: {e}")
