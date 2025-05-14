import sys
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from site_navigation import NAVIGATION_MAP, TARGET_KEYWORDS
load_dotenv()

import asyncio
import re

class Post(BaseModel):
    caption: str
    url: str

class Posts(BaseModel):
    posts: List[Post]

controller = Controller(output_model=Posts)

# Configure the browser to connect to your Chrome instance
browser = Browser(
    config=BrowserConfig(
        # Specify the path to your Chrome executable
        browser_binary_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    )
)

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')

def preprocess_task_with_navigation(task_description: str) -> str:
    """
    Revisa la tarea en busca de frases clave de navegación y las expande.
    """
    processed_task = task_description
    
    # Primero, normalizar frases clave si usas TARGET_KEYWORDS
    for alias, canonical_target in TARGET_KEYWORDS.items():
        # Usar regex para reemplazar alias cuidando palabras completas y casing
        pattern_alias = re.compile(r'\b' + re.escape(alias) + r'\b', re.IGNORECASE)
        if pattern_alias.search(processed_task):
            # Reemplaza el alias por el nombre canónico para que el siguiente loop lo encuentre
            # Esto es una simplificación. Una lógica más robusta podría ser necesaria
            # si el alias forma parte de una frase más larga que debe conservarse.
            # Por ahora, asumimos que el alias es el objetivo principal de la navegación.
            # Ejemplo: "ve al reporte de colas y haz X" -> "ve al reporte de colas en tiempo real y haz X"
             processed_task = pattern_alias.sub(canonical_target, processed_task)


    # Buscar frases como "Ve a [destino]", "Ingresa a [destino]", etc.
    # y reemplazar "[destino]" si está en NAVIGATION_MAP
    # Esta regex busca un verbo de acción, seguido de "a" o "al", y luego el destino.
    # (?:...) es un grupo sin captura.
    # \s+ significa uno o más espacios.
    # (.*?) captura el nombre del destino de forma no codiciosa.
    # re.IGNORECASE para no distinguir mayúsculas/minúsculas.
    
    # Intentamos encontrar un patrón como "Acción [preposición] [destino conocido]"
    # y reemplazarlo.
    for target_name_key, instructions in NAVIGATION_MAP.items():
        # Construimos un patrón para buscar la mención del destino.
        # Ejemplo: "Ve al reporte de colas en tiempo real y luego filtra..."
        # Queremos reemplazar "Ve al reporte de colas en tiempo real" con las instrucciones.
        
        # Patrones para identificar la frase de navegación que queremos reemplazar
        # Se flexible con las preposiciones y artículos (el, la, los, las)
        # El \b asegura que "colas" no coincida con "bicolas" (límite de palabra)
        action_phrases = [
            r"ir a(?:l)?\s+",
            r"ingresa(?:r)? a(?:l)?\s+",
            r"navega(?:r)? a(?:l)?\s+",
            r"accede(?:r)? a(?:l)?\s+",
            r"ve a(?:l)?\s+",
            r"visita(?:r)?\s+(?:el\s+|la\s+)?",
            r"en(?:cuentra)?\s+(?:el\s+|la\s+)?",
            r"muéstrame\s+(?:el\s+|la\s+)?",
            r"abre\s+(?:el\s+|la\s+)?"
        ]
        
        # Combinar frases de acción con el nombre del objetivo (escapado por seguridad)
        # y permitir algo de texto después (capturado por 'remaining_action')
        # Esto se vuelve complejo rápidamente. Un enfoque más simple: si se menciona el target_name_key,
        # y la frase parece ser una instrucción de navegación hacia él, se reemplaza.

        # Enfoque más simple y potencialmente más robusto para el reemplazo:
        # Si el nombre del destino (target_name_key) está en la tarea,
        # y parece ser el objetivo de una navegación, lo reemplazamos.
        # Esto es heurístico.
        
        # Buscamos el nombre del destino en la tarea.
        # Usamos re.escape para tratar caracteres especiales en target_name_key como literales.
        # \b para asegurar que sean palabras completas.
        target_pattern = re.compile(r'\b' + re.escape(target_name_key) + r'\b', re.IGNORECASE)
        match = target_pattern.search(processed_task)

        if match:
            # Encontramos el nombre del destino. Ahora intentamos ver si es una instrucción de navegación.
            # Buscamos si alguna de las "action_phrases" precede al destino.
            # Esto es una simplificación; una gramática más completa sería necesaria para perfección.
            # Por ejemplo, si la tarea es "Describe el reporte de colas en tiempo real", no queremos reemplazar.
            # Pero si es "Ve al reporte de colas en tiempo real y haz X", sí.

            # Heurística: si el target_name_key está al principio o después de una frase de acción.
            # Esto puede ser propenso a errores y necesitar ajustes.
            # Una forma más simple podría ser que el LLM refinador ya estructure la tarea como:
            # "OBJETIVO_NAVEGACION: [nombre canónico del destino]. ACCION: [lo que hay que hacer allí]"
            # Y aquí solo reemplazaríamos si encontramos "OBJETIVO_NAVEGACION: [nombre canónico del destino]".
            
            # Por ahora, una aproximación: si el `target_name_key` está presente,
            # asumimos que el LLM de refinamiento ya lo ha puesto en un contexto de navegación.
            # Prependemos las instrucciones y luego la tarea original, esperando que el LLM
            # del agente entienda que primero debe navegar y luego ejecutar el resto.

            # Si la tarea original era "Ve al reporte de colas en tiempo real y obtén los datos."
            # Y `target_name_key` es "reporte de colas en tiempo real"
            # Podríamos reemplazar `target_name_key` con las instrucciones, o una parte de la frase.
            
            # Intentemos reemplazar una frase que contenga el `target_name_key` y una acción previa.
            # Ejemplo: "(Acción) (a/al/el/la) (target_name_key)"
            # Esto requiere una regex más cuidadosa.

            # Alternativa: Si el LLM refinador produce "Ve a XYZ. Luego haz ABC."
            # Y "XYZ" es una clave en NAVIGATION_MAP.
            for action_prefix in action_phrases:
                # Patrón: (frase de acción)(destino conocido)(posible conector y resto de la tarea)
                # Ejemplo: "ve al reporte de colas en tiempo real y luego filtra los datos"
                # queremos reemplazar "ve al reporte de colas en tiempo real"
                regex_str = r"({})({})(.*)".format(action_prefix, re.escape(target_name_key), r"(\s+(?:y luego|y|,)\s+.*)?")
                full_pattern = re.compile(regex_str, re.IGNORECASE | re.DOTALL)
                
                # Intentar reemplazar la frase de navegación completa
                def replace_nav(match_obj):
                    # match_obj.group(1) es la frase de acción (ej. "ve al ")
                    # match_obj.group(2) es el target_name_key
                    # match_obj.group(3) es el resto de la tarea (ej. " y luego filtra los datos")
                    remaining_action = match_obj.group(3) if match_obj.group(3) else ""
                    # Limpiar el conector si existe para evitar duplicados (ej. "y luego")
                    remaining_action = re.sub(r"^\s*(?:y luego|y|,)\s*", "", remaining_action, flags=re.IGNORECASE).strip()
                    
                    # Si no hay acción restante, solo se navega.
                    if not remaining_action:
                         return f"{instructions}." # Solo navega
                    return f"{instructions}. Luego, {remaining_action}"

                processed_task, num_replacements = full_pattern.subn(replace_nav, processed_task, count=1)
                if num_replacements > 0:
                    print(f"--- Preprocesador: Ruta encontrada para '{target_name_key}'. Tarea modificada.")
                    return processed_task # Devolver tras el primer reemplazo exitoso

    print("--- Preprocesador: No se encontraron rutas directas. Usando tarea como está.")
    return processed_task

async def main_logic(task_description: str):
    processed_task_for_agent = preprocess_task_with_navigation(task_description)

    print(f"--- Tarea final para el agente: {processed_task_for_agent}")

    initial_actions = [
        {'open_tab': {'url': os.environ.get('YOIZEN_URL')}},
    ]
    sensitive_data = {'y_username': 'supertomi', 'y_password': 'Yoizen123'}
    login_credentials_prompt = (
        f"Realiza el login usando supertomi y Yoizen123 como usuario y contraseña. "
        "Asegúrate de que el login sea exitoso antes de continuar. "
        "Despues, segui las siguientes instrucciones: "
    )
    agent = Agent(
        task=login_credentials_prompt+processed_task_for_agent,
        llm=llm,
        browser=browser,
        controller=controller,
        initial_actions=initial_actions,
        sensitive_data=sensitive_data,
    )
    result = await agent.run()
    print(result.final_result())
    await browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_task = sys.argv[1]
    else:
        user_task = "Por favor, especifica una tarea. Ejemplo: al ingresar a example.com, dime el título de la página."
        print("Error: No se proporcionó ninguna tarea.", file=sys.stderr)
    asyncio.run(main_logic(user_task))