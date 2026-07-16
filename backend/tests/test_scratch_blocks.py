from app.llm.prompts import BIT_SYSTEM_PROMPT, build_reference_block, build_system_instruction
from app.llm.scratch_blocks import BLOCKS, parse_block_codes, render_bloques

# Los 12 códigos que hoy aparecen en juegos.bloques_clave deben estar en el diccionario.
CODIGOS_EN_USO = [
    "eventos_bandera_verde",
    "eventos_enviar_mensaje",
    "eventos_al_recibir_mensaje",
    "control_repetir_veces",
    "control_esperar_segundos",
    "movimiento_mover_pasos",
    "movimiento_cambiar_x",
    "movimiento_girar_derecha_grados",
    "movimiento_apuntar_direccion",
    "apariencia_decir_segundos",
    "apariencia_cambiar_fondo",
    "apariencia_siguiente_disfraz",
]


def test_todos_los_codigos_en_uso_estan_mapeados() -> None:
    for code in CODIGOS_EN_USO:
        assert code in BLOCKS, f"falta el bloque {code}"
        info = BLOCKS[code]
        assert info["etiqueta"] and info["categoria"] and info["color_hex"].startswith("#")


def test_parse_block_codes_desde_formato_de_la_base() -> None:
    raw = '"eventos_bandera_verde","control_repetir_veces","movimiento_mover_pasos"'
    assert parse_block_codes(raw) == [
        "eventos_bandera_verde",
        "control_repetir_veces",
        "movimiento_mover_pasos",
    ]
    assert parse_block_codes(None) == []
    assert parse_block_codes("") == []


def test_render_bloques_traduce_a_etiqueta_categoria_y_color() -> None:
    render = render_bloques('"control_repetir_veces"')
    assert '"repetir ()"' in render
    assert "Control" in render
    assert "naranja" in render


def test_render_bloques_codigo_desconocido_no_rompe() -> None:
    render = render_bloques('"bloque_que_no_existe"')
    assert "bloque que no existe" in render  # cae al texto limpio, sin lanzar


def test_reference_block_omite_datos_ausentes() -> None:
    solo_titulo = build_reference_block("Atrapa la estrella", None, None, None)
    assert "Atrapa la estrella" in solo_titulo
    assert "Solucion de referencia" not in solo_titulo
    assert "Bloques clave" not in solo_titulo
    assert "Video de ejemplo" not in solo_titulo


def test_reference_block_incluye_datos_presentes() -> None:
    ref = build_reference_block(
        "Haz bailar al gato",
        "El gato baila con un bucle.",
        '"control_repetir_veces"',
        "https://youtu.be/Sf4Dr52UElc",
    )
    assert "El gato baila con un bucle." in ref
    assert '"repetir ()"' in ref
    assert "https://youtu.be/Sf4Dr52UElc" in ref


def test_build_system_instruction_usa_prompt_base_por_defecto() -> None:
    instr = build_system_instruction("Juego X", None, None, None, base_prompt="prompt corto")
    # el prompt base generico (corto) se descarta a favor del prompt fuerte de Bit
    assert BIT_SYSTEM_PROMPT[:60] in instr
    assert "REFERENCIA DEL JUEGO" in instr
