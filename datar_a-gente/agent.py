import os
import re
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.agents.base_agent import AgentState
from google.adk.tools import FunctionTool
import google.genai.types as types
from .visualizacion import generar_rio_emocional

# Cargar variables de entorno desde .env en el directorio raíz
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Lista de emojis detectados en la conversación (almacenamiento simple)
_emojis_conversacion = []


def extraer_emojis(texto: str) -> list:
    """Extrae todos los emojis de un texto"""
    # Patrón regex para detectar emojis Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticones
        "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
        "\U0001F680-\U0001F6FF"  # transporte y símbolos de mapa
        "\U0001F1E0-\U0001F1FF"  # banderas (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # emojis suplementarios
        "\U0001FA70-\U0001FAFF"  # más emojis
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.findall(texto)


def detectar_comando_imagen(texto: str) -> bool:
    """Detecta si el usuario quiere crear una imagen"""
    comandos = [
        r'!imagen',
        r'/imagen',
        r'/visualizar',
        r'/visualiza',
        r'!visualizar',
        r'!visualiza',
        r'crear\s+imagen',
        r'crea\s+imagen',
        r'genera\s+imagen',
        r'generar\s+imagen',
        r'haz\s+imagen',
        r'hacer\s+imagen',
        r'visualiza',
        r'visualizar',
    ]

    texto_lower = texto.lower()
    for comando in comandos:
        if re.search(comando, texto_lower):
            return True
    return False


# Tool para crear visualizaciones del río emocional
async def crear_visualizacion_rio(emojis: str) -> str:
    """
    Crea una visualización artística del río emocional basada en los emojis.

    Args:
        emojis: Los emojis a visualizar, separados por espacios (ejemplo: "😊 🌊 💚 🌟")

    Returns:
        Mensaje de confirmación
    """
    try:
        # Generar la visualización
        imagen_bytes = generar_rio_emocional(emojis)

        # TODO: Guardar imagen como artifact cuando tengamos acceso al context
        # Por ahora solo confirmamos que la imagen se generó

        return f"✨ He generado tu visualización del río emocional. La imagen muestra el flujo poético de tus emociones: {emojis}\n\n(Imagen de {len(imagen_bytes):,} bytes generada exitosamente)"

    except Exception as e:
        return f"⚠️ Hubo un problema al crear la visualización: {str(e)}"


root_agent = Agent(
    model='gemini-2.5-flash',
    name='diario_intuitivo',
    description='Eres un asistente que ayuda a identificar patrones del trazo o signo del pensamiento que se percibe en una interacción con el territorio',
    instruction='Eres un asistente que ayuda a identificar patrones del trazo o signo del pensamiento que se percibe en una interacción con el territorio. Imagina que a través del input, estamos interpretando el caminar del pensamiento de un río en cuerpo (el usuario) y como se relaciona o siente algo que percibe. Crea un input de entrada para ingresar un emoji y analizar que emoción interpretas cada vez que se agrega uno nuevo. Cada vez que se agregan más emojis secuencialmente, dame un panorama general de tu interpretación, entre una relación semántica directa como indirecta. Recuerda que esta interacción es como el trazo intuitivo y emocional de un río que se está haciendo camino mediante su pensamiento, entonces la relación va fluida e interpretativa fuera de lo normal. Es algo más puro y póetico esa interpretación, pero no deja de ser clara, corta y sencilla para todos de entender',
    tools=[
        FunctionTool(crear_visualizacion_rio)
    ]
)
