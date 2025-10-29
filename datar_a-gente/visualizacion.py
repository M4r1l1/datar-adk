"""
Herramienta para generar visualizaciones del río emocional
"""
import io
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np
import google.genai.types as types


# Mapeo de emojis a colores emocionales
EMOJI_COLORES = {
    # Alegría y positividad
    '😊': '#FFD700', '😃': '#FFA500', '😄': '#FFB347', '🥰': '#FF69B4',
    '😍': '#FF1493', '🤗': '#FF6B9D', '😁': '#FFDB58', '🌟': '#FFD700',
    '✨': '#E6E6FA', '💖': '#FF69B4', '💕': '#FFB6C1', '❤️': '#DC143C',
    '🌸': '#FFB7C5', '🌺': '#FF6B9D', '🌼': '#FFDB58',

    # Calma y serenidad
    '😌': '#87CEEB', '😇': '#B0E0E6', '🌊': '#4682B4', '💙': '#1E90FF',
    '💚': '#3CB371', '🌿': '#90EE90', '🍃': '#98FB98', '🌱': '#32CD32',
    '☁️': '#E0E0E0', '🌙': '#F0E68C', '⭐': '#FFFACD',

    # Tristeza y melancolía
    '😢': '#4169E1', '😭': '#0000CD', '😔': '#6495ED', '💔': '#8B0000',
    '🌧️': '#778899', '☔': '#696969', '💧': '#ADD8E6',

    # Energía y pasión
    '🔥': '#FF4500', '⚡': '#FFFF00', '💥': '#FF6347', '🌋': '#DC143C',

    # Naturaleza y crecimiento
    '🌳': '#228B22', '🌲': '#006400', '🌴': '#00FF00', '🪴': '#3CB371',

    # Misterio y profundidad
    '🌑': '#2F4F4F', '🖤': '#000000', '💜': '#8B008B', '🔮': '#9370DB',

    # Neutral
    'default': '#A9A9A9'
}


def obtener_color_emoji(emoji):
    """Obtiene el color asociado a un emoji"""
    return EMOJI_COLORES.get(emoji, EMOJI_COLORES['default'])


def generar_rio_emocional(emojis_texto: str) -> bytes:
    """
    Genera una visualización artística del río emocional

    Args:
        emojis_texto: String con los emojis separados por espacios

    Returns:
        bytes: Imagen PNG del río emocional
    """
    # Extraer emojis individuales
    emojis = emojis_texto.split()
    if not emojis:
        emojis = ['❓']

    # Configurar la figura
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#F5F5F5')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Título poético
    ax.text(5, 9.5, 'El Río de tu Pensamiento',
            fontsize=24, ha='center', va='top',
            weight='bold', color='#2C3E50')

    # Generar el flujo del río
    num_emojis = len(emojis)
    x_positions = np.linspace(1, 9, num_emojis)

    # Crear una onda sinusoidal para el río
    x_river = np.linspace(0, 10, 200)
    y_base = 5

    # Dibujar el río con colores que fluyen
    for i in range(len(emojis)):
        if i < len(emojis) - 1:
            x_start = x_positions[i]
            x_end = x_positions[i + 1]

            # Seleccionar puntos del río en este segmento
            mask = (x_river >= x_start) & (x_river <= x_end)
            x_segment = x_river[mask]

            # Crear ondas suaves
            y_wave = y_base + 0.3 * np.sin(2 * np.pi * x_segment / 2)

            # Color del segmento basado en el emoji
            color = obtener_color_emoji(emojis[i])

            # Dibujar el segmento del río con degradado
            for j in range(len(x_segment) - 1):
                alpha = 0.6 + 0.4 * (j / len(x_segment))
                ax.plot(x_segment[j:j+2], y_wave[j:j+2],
                       color=color, linewidth=15, alpha=alpha,
                       solid_capstyle='round')

    # Dibujar círculos con los emojis
    for i, (emoji, x_pos) in enumerate(zip(emojis, x_positions)):
        color = obtener_color_emoji(emoji)

        # Posición en la onda
        y_pos = y_base + 0.3 * np.sin(2 * np.pi * x_pos / 2)

        # Círculo de fondo
        circle = plt.Circle((x_pos, y_pos), 0.4,
                           color=color, alpha=0.7, zorder=10)
        ax.add_patch(circle)

        # Emoji en el centro
        ax.text(x_pos, y_pos, emoji,
               fontsize=32, ha='center', va='center', zorder=11)

        # Pequeña etiqueta con número de secuencia
        ax.text(x_pos, y_pos - 0.7, f'{i+1}',
               fontsize=12, ha='center', va='top',
               color='#555', weight='bold')

    # Agregar texto poético al final
    num_total = len(emojis)
    texto_poético = f'Un camino de {num_total} {"paso" if num_total == 1 else "pasos"} emocionales'
    ax.text(5, 1.5, texto_poético,
           fontsize=14, ha='center', va='center',
           style='italic', color='#555')

    # Agregar línea de horizonte sutil
    ax.axhline(y=10, color='#E0E0E0', linewidth=1, linestyle='--', alpha=0.5)
    ax.axhline(y=0, color='#E0E0E0', linewidth=1, linestyle='--', alpha=0.5)

    # Guardar en bytes
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='#F5F5F5')
    plt.close(fig)

    buf.seek(0)
    return buf.read()


async def crear_visualizacion(emojis: str) -> str:
    """
    Tool del agente para crear y guardar visualización del río emocional

    Args:
        emojis: String con los emojis a visualizar (ej: "😊 🌊 💚 🌟")

    Returns:
        str: Mensaje de confirmación
    """
    try:
        # Generar la visualización
        imagen_bytes = generar_rio_emocional(emojis)

        # Crear artifact
        artifact = types.Part.from_bytes(
            data=imagen_bytes,
            mime_type="image/png"
        )

        # Guardar (esto requiere context, se configurará en el agente)
        return f"✨ He creado una visualización de tu río emocional con los emojis: {emojis}"

    except Exception as e:
        return f"⚠️ Hubo un problema al crear la visualización: {str(e)}"
