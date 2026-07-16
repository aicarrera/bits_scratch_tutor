"""Diccionario de bloques de Scratch 3.0 en español (código → etiqueta real).

Generado y verificado adversarialmente por un workflow multi-agente.
Los `code` siguen la convención `categoria_accion` usada en juegos.bloques_clave.
La `etiqueta` es el texto REAL del bloque en el editor de Scratch en español,
con `()` donde el bloque tiene un hueco editable. Sirve para que el tutor Bit
nombre los bloques como el niño los ve, en vez del código interno.
"""

from __future__ import annotations

import re


# Nombre del color de cada categoría, tal como se lo describimos al niño.
CATEGORY_COLOR_NAME: dict[str, str] = {
    "Movimiento": "azul",
    "Apariencia": "morado",
    "Sonido": "rosa",
    "Eventos": "amarillo",
    "Control": "naranja",
    "Sensores": "celeste",
    "Operadores": "verde",
    "Variables": "naranja oscuro",
}


# code -> {etiqueta, categoria, color_hex}
BLOCKS: dict[str, dict[str, str]] = {
    "apariencia_cambiar_disfraz": {"etiqueta": "cambiar disfraz a ()", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_cambiar_fondo": {"etiqueta": "cambiar fondo a ()", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_cambiar_tamano": {"etiqueta": "cambiar tamaño por ()", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_decir": {"etiqueta": "decir ()", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_decir_segundos": {"etiqueta": "decir () durante () segundos", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_esconder": {"etiqueta": "esconder", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_fijar_tamano": {"etiqueta": "fijar tamaño al () %", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_mostrar": {"etiqueta": "mostrar", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_pensar": {"etiqueta": "pensar ()", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_pensar_segundos": {"etiqueta": "pensar () durante () segundos", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_siguiente_disfraz": {"etiqueta": "siguiente disfraz", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "apariencia_siguiente_fondo": {"etiqueta": "siguiente fondo", "categoria": "Apariencia", "color_hex": "#9966FF"},
    "control_crear_clon_de": {"etiqueta": "crear clon de ()", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_detener": {"etiqueta": "detener ()", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_eliminar_este_clon": {"etiqueta": "eliminar este clon", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_esperar_hasta_que": {"etiqueta": "esperar hasta que ()", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_esperar_segundos": {"etiqueta": "esperar () segundos", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_por_siempre": {"etiqueta": "por siempre", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_repetir_hasta_que": {"etiqueta": "repetir hasta que ()", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_repetir_veces": {"etiqueta": "repetir ()", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_si_entonces": {"etiqueta": "si () entonces", "categoria": "Control", "color_hex": "#FFAB19"},
    "control_si_entonces_si_no": {"etiqueta": "si () entonces si no", "categoria": "Control", "color_hex": "#FFAB19"},
    "eventos_al_cambiar_fondo": {"etiqueta": "cuando el fondo cambie a (fondo1)", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "eventos_al_hacer_clic_objeto": {"etiqueta": "al hacer clic en este objeto", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "eventos_al_presionar_tecla": {"etiqueta": "al presionar tecla (espacio)", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "eventos_al_recibir_mensaje": {"etiqueta": "al recibir (mensaje1)", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "eventos_al_superar": {"etiqueta": "al superar (volumen) > (10)", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "eventos_bandera_verde": {"etiqueta": "al hacer clic en 🏳", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "eventos_enviar_mensaje": {"etiqueta": "enviar (mensaje1)", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "eventos_enviar_mensaje_y_esperar": {"etiqueta": "enviar (mensaje1) y esperar", "categoria": "Eventos", "color_hex": "#FFBF00"},
    "movimiento_apuntar_direccion": {"etiqueta": "apuntar en dirección ()", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_apuntar_hacia": {"etiqueta": "apuntar hacia ()", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_cambiar_x": {"etiqueta": "cambiar x por ()", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_cambiar_y": {"etiqueta": "sumar () a y", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_deslizar_xy": {"etiqueta": "deslizar en () segundos a x: () y: ()", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_fijar_x": {"etiqueta": "fijar x a ()", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_fijar_y": {"etiqueta": "fijar y a ()", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_girar_derecha_grados": {"etiqueta": "girar ↻ () grados", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_girar_izquierda_grados": {"etiqueta": "girar ↺ () grados", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_ir_a_xy": {"etiqueta": "ir a x: () y: ()", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_mover_pasos": {"etiqueta": "mover () pasos", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "movimiento_rebotar_borde": {"etiqueta": "si toca un borde, rebotar", "categoria": "Movimiento", "color_hex": "#4C97FF"},
    "operadores_dividir": {"etiqueta": "() / ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_igual": {"etiqueta": "() = ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_mayor_que": {"etiqueta": "() > ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_menor_que": {"etiqueta": "() < ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_multiplicar": {"etiqueta": "() * ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_no": {"etiqueta": "no ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_numero_aleatorio": {"etiqueta": "número aleatorio entre () y ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_o": {"etiqueta": "() o ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_restar": {"etiqueta": "() - ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_sumar": {"etiqueta": "() + ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_unir": {"etiqueta": "unir () y ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "operadores_y": {"etiqueta": "() y ()", "categoria": "Operadores", "color_hex": "#59C059"},
    "sensores_cronometro": {"etiqueta": "cronómetro", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_distancia_a": {"etiqueta": "distancia a ()", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_preguntar_esperar": {"etiqueta": "preguntar () y esperar", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_raton_presionado": {"etiqueta": "¿ratón presionado?", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_raton_x": {"etiqueta": "ratón en x", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_raton_y": {"etiqueta": "posición y del ratón", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_reiniciar_cronometro": {"etiqueta": "reiniciar cronómetro", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_respuesta": {"etiqueta": "respuesta", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_tecla_presionada": {"etiqueta": "¿tecla () presionada?", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_tocando": {"etiqueta": "¿tocando ()?", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_tocando_color": {"etiqueta": "¿tocando el color ()?", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sensores_volumen": {"etiqueta": "volumen del sonido", "categoria": "Sensores", "color_hex": "#5CB1D6"},
    "sonido_cambiar_efecto": {"etiqueta": "cambiar efecto () por ()", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_cambiar_volumen": {"etiqueta": "cambiar volumen en ()", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_detener_todos": {"etiqueta": "detener todos los sonidos", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_fijar_efecto": {"etiqueta": "fijar efecto () a ()", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_fijar_volumen": {"etiqueta": "fijar volumen a () %", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_iniciar": {"etiqueta": "iniciar sonido ()", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_quitar_efectos": {"etiqueta": "quitar efectos de sonido", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_reproducir_hasta_terminar": {"etiqueta": "tocar sonido () hasta que termine", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "sonido_volumen": {"etiqueta": "volumen", "categoria": "Sonido", "color_hex": "#CF63CF"},
    "variables_anadir_a_lista": {"etiqueta": "añadir () a ()", "categoria": "Variables", "color_hex": "#FF661A"},
    "variables_borrar_de_lista": {"etiqueta": "borrar () de ()", "categoria": "Variables", "color_hex": "#FF8C1A"},
    "variables_borrar_todo_lista": {"etiqueta": "borrar todo de ()", "categoria": "Variables", "color_hex": "#FF661A"},
    "variables_cambiar_por": {"etiqueta": "cambiar () por ()", "categoria": "Variables", "color_hex": "#FF8C1A"},
    "variables_elemento_de_lista": {"etiqueta": "elemento () de ()", "categoria": "Variables", "color_hex": "#FF661A"},
    "variables_esconder_variable": {"etiqueta": "esconder variable ()", "categoria": "Variables", "color_hex": "#FF8C1A"},
    "variables_lista_contiene": {"etiqueta": "() contiene ()?", "categoria": "Variables", "color_hex": "#FF8C1A"},
    "variables_longitud_lista": {"etiqueta": "longitud de ()", "categoria": "Variables", "color_hex": "#FF661A"},
    "variables_mostrar_variable": {"etiqueta": "mostrar variable ()", "categoria": "Variables", "color_hex": "#FF8C1A"},
    "variables_poner_a": {"etiqueta": "dar a () el valor ()", "categoria": "Variables", "color_hex": "#FF8C1A"},
    "variables_valor": {"etiqueta": "mi variable", "categoria": "Variables", "color_hex": "#FF8C1A"},
}


_CODE_RE = re.compile(r"[a-z][a-z0-9_]+")


def parse_block_codes(raw: str | None) -> list[str]:
    """Extrae los códigos de bloque de un valor `bloques_clave`.

    Acepta el formato guardado en la base ('"a","b"'), una lista JSON o texto
    suelto: toma cualquier token con forma de código y conserva el orden y las
    repeticiones no."""
    if not raw:
        return []
    codes: list[str] = []
    for token in _CODE_RE.findall(raw):
        if token not in codes:
            codes.append(token)
    return codes


def render_bloques(raw: str | None) -> str:
    """Convierte `bloques_clave` en una lista legible para el prompt del tutor.

    Cada bloque conocido se muestra con su etiqueta real de Scratch, su categoría
    y el nombre de su color. Los códigos desconocidos se listan tal cual para no
    perder información. Devuelve "" si no hay bloques."""
    codes = parse_block_codes(raw)
    if not codes:
        return ""
    lineas: list[str] = []
    for code in codes:
        info = BLOCKS.get(code)
        if info is None:
            lineas.append(f'- "{code.replace(chr(95), chr(32))}"')
            continue
        color = CATEGORY_COLOR_NAME.get(info["categoria"], info["color_hex"])
        lineas.append(
            f'- "{info["etiqueta"]}" (categoría {info["categoria"]}, {color})'
        )
    return "\n".join(lineas)
