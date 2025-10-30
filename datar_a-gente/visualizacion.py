"""
Herramienta para generar visualizaciones del río emocional
"""
import io
import os
from datetime import datetime
from pathlib import Path as FilePath
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


#---- Aquí empezó la prueba usando Numpy/Pillow  ----#
#---- Aquí empezó la prueba usando Numpy/Pillow  ----#
#---- Aquí empezó la prueba usando Numpy/Pillow  ----#

def interpretar_texto_a_parametros(texto: str) -> dict:
    """
    Interpreta un texto de manera abstracta y lo convierte en parámetros matemáticos

    Args:
        texto: El texto a interpretar

    Returns:
        dict: Diccionario con parámetros matemáticos interpretados
    """
    # Análisis básico del texto
    longitud = len(texto)
    vocales = sum(1 for c in texto.lower() if c in 'aeiouáéíóú')
    consonantes = sum(1 for c in texto.lower() if c.isalpha() and c not in 'aeiouáéíóú')
    espacios = texto.count(' ')
    palabras = len(texto.split())

    # Calcular "intensidad emocional" basada en puntuación
    signos_exclamacion = texto.count('!')
    signos_pregunta = texto.count('?')
    signos_puntos = texto.count('.')

    # Crear semilla única basada en el texto para reproducibilidad
    semilla = sum(ord(c) for c in texto) % 10000

    return {
        'longitud': longitud,
        'vocales': vocales,
        'consonantes': consonantes,
        'espacios': espacios,
        'palabras': palabras,
        'intensidad': signos_exclamacion * 1.5 + signos_pregunta * 0.8, # Más peso a exclamación
        'calma': signos_puntos * 0.7, # Más puntos = más calma
        'frecuencia_onda': max(0.5, vocales / 7),  # Más vocales = más ondas base
        'amplitud_onda': max(0.1, consonantes / 15),  # Más consonantes = más amplitud base
        'num_puntos': max(300, longitud * 15),  # Más texto = más puntos totales para detalle
        'semilla': semilla,
    }


def generar_puntos_numpy(parametros: dict, img_width: int, img_height: int) -> list[list[tuple[int, int]]]:
    """
    Genera puntos usando NumPy basándose en los parámetros interpretados,
    dividido en fases narrativas con lógica ajustada a la emoción.

    Args:
        parametros: Diccionario con parámetros matemáticos
        img_width (int): Ancho del canvas para límites.
        img_height (int): Alto del canvas para límites.

    Returns:
        list: Una lista de listas de tuplas (x, y), donde cada sublista
              representa los puntos para una "cinta" individual del trazo.
    """
    np.random.seed(parametros['semilla'])

    # Normalizar intensidad y calma para que estén en un rango manejable (0-1)
    # Ajustar estos valores máximos según la escala esperada de tus parámetros
    max_intensidad = 10 # Si la intensidad calculada puede llegar a 10
    max_calma = 5    # Si la calma calculada puede llegar a 5

    norm_intensidad = np.clip(parametros['intensidad'] / max_intensidad, 0, 1)
    norm_calma = np.clip(parametros['calma'] / max_calma, 0, 1)

    # --- Configuración global del trazo ---
    num_puntos_total = parametros['num_puntos']
    num_ribbons = int(3 + norm_intensidad * 4 + (1 - norm_calma) * 2) # Más cintas con intensidad, menos con calma (zigzagueo)
    ribbon_spacing_base = 3 + (norm_intensidad * 4) + (1 - norm_calma) * 2 # Espaciado base, más amplio si intenso o incierto
    
    # Punto de inicio aleatorio, pero en la parte inferior del canvas
    # Influenciado por la calma y intensidad para un inicio más "pensado" o "impulsivo"
    start_x = np.random.randint(img_width // 4, img_width // 2 + int(norm_intensidad * 100 - norm_calma * 50))
    start_y = np.random.randint(img_height - 150 - int(norm_intensidad * 50), img_height - 50 + int(norm_calma * 50))
    current_x, current_y = start_x, start_y

    all_main_trace_points = [] # Puntos principales del trazo para todas las fases

    # --- Definición de Fases ---
    # Los coeficientes son "mágicos" y ajustados para dar el efecto deseado
    
    # Fase 1: Acelera con decisión (🏃🏼‍♀️)
    # Impulso claro, ondulaciones moderadas pero consistentes.
    # Impulso mayor con intensidad, menor con calma. Amplitud más cerrada con intensidad. Frecuencia mayor con intensidad.
    num_puntos_fase1 = int(num_puntos_total * (0.25 + norm_intensidad * 0.1 - norm_calma * 0.05)) # Más larga con intensidad
    num_puntos_fase1 = np.clip(num_puntos_fase1, 50, num_puntos_total // 2)
    
    avance_x1 = (2 + norm_intensidad * 3) * (1 - norm_calma * 0.5) # Más impulso con intensidad, menos con calma
    avance_y1 = (-3 - norm_intensidad * 3) * (1 - norm_calma * 0.5)
    amplitud_onda1 = parametros['amplitud_onda'] * (1 - norm_intensidad * 0.7) + norm_calma * 15 # Más cerrada con intensidad, más abierta con calma
    frecuencia_onda1 = parametros['frecuencia_onda'] * (1 + norm_intensidad * 0.8) * (1 - norm_calma * 0.4) # Mayor con intensidad, menor con calma
    ruido_aleatorio1 = (10 + norm_intensidad * 10) * (1 - norm_calma * 0.5) # Más ruido con intensidad, menos con calma


    # Fase 2: Estallido de alegría (🎉) / Expansión, dispersión
    # Mayor amplitud y frecuencia, giros más amplios, posible "expansión" lateral.
    # Impulso muy fuerte con intensidad, baja con calma. Amplitud muy abierta con calma, más cerrada pero dispersa con intensidad.
    num_puntos_fase2 = int(num_puntos_total * (0.35 + norm_intensidad * 0.2 - norm_calma * 0.1)) # Más larga con intensidad
    num_puntos_fase2 = np.clip(num_puntos_fase2, 50, num_puntos_total // 2)

    avance_x2 = (1.5 + norm_intensidad * 2) * (1 - norm_calma * 0.3)
    avance_y2 = (-2.5 - norm_intensidad * 2) * (1 - norm_calma * 0.3)
    amplitud_onda2 = parametros['amplitud_onda'] * (1 - norm_intensidad * 0.3) + norm_calma * 30 # Más abierta con calma, pero "dispersa" con intensidad
    frecuencia_onda2 = parametros['frecuencia_onda'] * (1 + norm_intensidad * 1.5) * (1 - norm_calma * 0.2) # Mucho mayor con intensidad
    ruido_aleatorio2 = (25 + norm_intensidad * 30) * (1 + (1 - norm_calma) * 0.5) # Mucho ruido, especialmente con intensidad y poca calma


    # Fase 3: Se contrae con delicadeza / Incertidumbre (🤏🏽)
    # Ralentiza, zigzaguea si hay poca calma, grosor disminuye.
    # Impulso bajo. Amplitud muy cerrada con intensidad, más abierta con calma. Frecuencia alta con incertidumbre.
    num_puntos_fase3 = num_puntos_total - num_puntos_fase1 - num_puntos_fase2
    num_puntos_fase3 = max(10, num_puntos_fase3) # Al menos 10 puntos

    avance_x3 = (0.5 + (1 - norm_calma) * 1.5) * (1 - norm_intensidad * 0.3) # Más errático sin calma
    avance_y3 = (-0.5 - (1 - norm_calma) * 1.5) * (1 - norm_intensidad * 0.3)
    amplitud_onda3 = parametros['amplitud_onda'] * (1 - norm_intensidad * 0.9) + (1 - norm_calma) * 10 # Muy cerrada con intensidad, abierta y zigzagueante con incertidumbre
    frecuencia_onda3 = parametros['frecuencia_onda'] * (1 + (1 - norm_calma) * 2 + norm_intensidad * 0.5) # Muy alta con incertidumbre
    ruido_aleatorio3 = (15 + (1 - norm_calma) * 20) * (1 + norm_intensidad * 0.5) # Mucho ruido con incertidumbre


    # --- Generación de Puntos por Fases ---
    phases_params = [
        (num_puntos_fase1, avance_x1, avance_y1, amplitud_onda1, frecuencia_onda1, ruido_aleatorio1),
        (num_puntos_fase2, avance_x2, avance_y2, amplitud_onda2, frecuencia_onda2, ruido_aleatorio2),
        (num_puntos_fase3, avance_x3, avance_y3, amplitud_onda3, frecuencia_onda3, ruido_aleatorio3),
    ]

    wave_offset = 0 # Para un desplazamiento continuo de la onda

    for i_phase, (n_puntos, av_x, av_y, amp_onda, freq_onda, ruido) in enumerate(phases_params):
        for i in range(n_puntos):
            # La "huella de río" se logra con el ruido y las ondulaciones variables.
            # No es una frecuencia pura, sino un patrón de movimiento.
            
            # Frecuencia base aleatoria, influenciada por la emoción
            random_freq_factor = (0.8 + np.random.rand() * 0.4) # Variación aleatoria
            current_freq_x = freq_onda * 0.05 * random_freq_factor
            current_freq_y = freq_onda * 0.03 * random_freq_factor

            onda_x = amp_onda * np.sin((i + wave_offset) * current_freq_x)
            onda_y = amp_onda * np.cos((i + wave_offset) * current_freq_y)

            dx = av_x + np.random.normal(0, ruido / 10) + onda_x
            dy = av_y + np.random.normal(0, ruido / 10) + onda_y

            current_x += dx
            current_y += dy
            
            # Asegurar que el trazo permanezca dentro de límites razonables
            current_x = np.clip(current_x, 50, img_width - 50)
            current_y = np.clip(current_y, 50, img_height - 50)

            all_main_trace_points.append((int(current_x), int(current_y)))
        
        wave_offset += n_puntos # Para que la onda siga desde donde quedó

    # --- Generar las "cintas" paralelas ---
    all_ribbon_points = [[] for _ in range(num_ribbons)]

    if len(all_main_trace_points) < 2:
        return all_ribbon_points # No hay suficientes puntos para dibujar

    for i in range(len(all_main_trace_points)):
        p_curr_x, p_curr_y = all_main_trace_points[i]

        # Calcular el vector dirección y el vector normal (perpendicular)
        if i > 0:
            p_prev_x, p_prev_y = all_main_trace_points[i-1]
            vec_x = p_curr_x - p_prev_x
            vec_y = p_curr_y - p_prev_y
            
            length = np.sqrt(vec_x**2 + vec_y**2)
            if length > 0.1: # Evitar división por cero o por valores muy pequeños
                norm_x = -vec_y / length # Perpendicular normalizado
                norm_y = vec_x / length
            else: # Puntos coincidentes o muy cercanos, usar la normal anterior o por defecto
                if i > 1: # Usar la normal del segmento anterior si es posible
                    prev_norm_x, prev_norm_y = all_ribbon_points[0][i-1][0] - all_main_trace_points[i-1][0], \
                                                all_ribbon_points[0][i-1][1] - all_main_trace_points[i-1][1]
                    norm_length = np.sqrt(prev_norm_x**2 + prev_norm_y**2)
                    if norm_length > 0:
                        norm_x, norm_y = prev_norm_x / norm_length, prev_norm_y / norm_length
                    else:
                        norm_x, norm_y = 1, 0 # Fallback
                else:
                    norm_x, norm_y = 1, 0 # Fallback inicial
        else: # Primer punto, asumir una dirección inicial (ej. horizontal para el perpendicular)
            norm_x, norm_y = 1, 0 

        for r in range(num_ribbons):
            displacement = (r - num_ribbons / 2) * (ribbon_spacing_base + norm_intensidad * 5 - norm_calma * 2) # Espaciado influenciado

            ribbon_points_x = int(p_curr_x + norm_x * displacement)
            ribbon_points_y = int(p_curr_y + norm_y * displacement)
            all_ribbon_points[r].append((ribbon_points_x, ribbon_points_y))

    return all_ribbon_points


def generar_imagen_texto(texto: str) -> Image.Image:
    """
    Genera una imagen interpretativa del texto usando Pillow,
    con el trazo dividido en fases narrativas y grosor dinámico.

    Args:
        texto: El texto a visualizar

    Returns:
        Image: Imagen PIL generada
    """
    # Interpretar el texto
    parametros = interpretar_texto_a_parametros(texto)

    # Crear canvas
    width, height = 1000, 700 # Ajustado a un tamaño más común
    imagen = Image.new('RGB', (width, height), color='#F5F5F5')
    draw = ImageDraw.Draw(imagen)

    # Generar puntos con NumPy (ahora devuelve una lista de listas para las cintas)
    all_ribbon_points = generar_puntos_numpy(parametros, width, height)

    # --- Título ---
    titulo = "Trazo del Pensamiento"
    try:
        from PIL import ImageFont
        font_path = "arial.ttf" # Asegúrate de que esta fuente exista o usa una por defecto
        try:
            font = ImageFont.truetype(font_path, 24)
        except IOError:
            font = ImageFont.load_default() # Fallback
    except ImportError:
        font = ImageFont.load_default()

    draw.text((width // 2, 30), titulo, fill="#000000", anchor='mm', font=font)


    # --- Dibujar las "cintas" con grosor y color dinámico ---
    if not all_ribbon_points or not all_ribbon_points[0]:
        print("No hay puntos para dibujar. Verifique la generación de puntos.")
        draw.text((width // 2, height // 2), "No se pudo generar el trazo", fill="#FF0000", anchor='mm', font=font)
        return imagen

    # Normalizar intensidad y calma para el grosor
    max_intensidad = 10
    max_calma = 5
    norm_intensidad = np.clip(parametros['intensidad'] / max_intensidad, 0, 1)
    norm_calma = np.clip(parametros['calma'] / max_calma, 0, 1)

    base_width_individual_ribbon = 1 # Grosor base de cada línea paralela
    
    # El grosor total del "río" o "huella" varía
    # Más ancho si hay intensidad (fuerza) o menos calma (incertidumbre)
    # Más delgado si hay mucha calma
    overall_width_factor = 1 + norm_intensidad * 2 + (1 - norm_calma) * 1.5

    # Recorrer cada "cinta"
    for r_idx, ribbon_points in enumerate(all_ribbon_points):
        if len(ribbon_points) < 2:
            continue
        
        for i in range(len(ribbon_points) - 1):
            # Grosor dinámico: varía con la intensidad/calma y también a lo largo del trazo
            dynamic_width = base_width_individual_ribbon * overall_width_factor

            # Reducir el grosor hacia el final si hay baja calma (incertidumbre)
            # Esto simula el "desvanecimiento" o la "contracción" al final
            if i > len(ribbon_points) * 0.7:
                 # Factor de reducción lineal desde 70% del trazo hasta el final
                 reduction_factor = (1 - (i - len(ribbon_points) * 0.7) / (len(ribbon_points) * 0.3))
                 dynamic_width *= reduction_factor * (1 + (1 - norm_calma) * 2) # Más reducción si hay incertidumbre

            dynamic_width = max(1, int(dynamic_width)) # Grosor mínimo de 1

            color_trazo = "black" # Mantener negro para el estilo de referencia

            draw.line([ribbon_points[i], ribbon_points[i + 1]], fill=color_trazo, width=dynamic_width, joint="curve")

    # Fecha y hora de creación en la parte inferior
    fecha_hora = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    draw.text((width // 2, height - 20), fecha_hora, fill='#555', anchor='mm', font=font)

    return imagen

#---- Aquí terminó la prueba usando Numpy/Pillow  ----#
#---- Aquí terminó la prueba usando Numpy/Pillow  ----#
#---- Aquí terminó la prueba usando Numpy/Pillow  ----#



def guardar_imagen_texto(texto: str) -> str:
    """
    Genera y guarda una imagen interpretativa del texto

    Args:
        texto: El texto a visualizar

    Returns:
        str: Ruta donde se guardó la imagen
    """
    # Generar la imagen
    imagen = generar_imagen_texto(texto)

    # Crear nombre de archivo único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"trazo_{timestamp}.png"

    # Determinar ruta de guardado
    proyecto_root = FilePath(__file__).parent.parent
    carpeta_imagenes = proyecto_root / "imagenes_generadas"
    carpeta_imagenes.mkdir(exist_ok=True)

    ruta_completa = carpeta_imagenes / nombre_archivo

    # Guardar imagen
    imagen.save(ruta_completa, 'PNG')

    return str(ruta_completa)
