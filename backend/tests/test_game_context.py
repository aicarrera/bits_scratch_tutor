from types import SimpleNamespace

from app.llm.catalog import build_game_context, load_bloques, parse_block_codes


def _game(**kwargs):
    base = {
        "titulo": "Juego X",
        "descripcion_solucion": None,
        "bloques_clave": None,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def _version(**kwargs):
    base = {"instruccion_nino": "Haz algo", "objetivos_pedagogicos": [], "pistas_progresivas": []}
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_parse_block_codes_desde_formato_de_la_base() -> None:
    raw = '"eventos_bandera_verde","control_repetir_veces","movimiento_mover_pasos"'
    assert parse_block_codes(raw) == [
        "eventos_bandera_verde",
        "control_repetir_veces",
        "movimiento_mover_pasos",
    ]
    assert parse_block_codes(None) == []
    assert parse_block_codes("") == []


def test_context_omite_solucion_y_bloques_cuando_faltan() -> None:
    data = load_bloques()
    ctx = build_game_context(_game(), _version(), data)
    assert "Juego X" in ctx
    assert "SOLUCIÓN DE REFERENCIA" not in ctx
    assert "BLOQUES CLAVE" not in ctx


def test_context_incluye_solucion_y_traduce_bloques() -> None:
    data = load_bloques()
    game = _game(
        titulo="Haz bailar al gato",
        descripcion_solucion="El gato se mueve con un bucle y gira.",
        bloques_clave='"eventos_bandera_verde","control_repetir_veces"',
    )
    ctx = build_game_context(game, _version(), data)
    assert "SOLUCIÓN DE REFERENCIA" in ctx
    assert "El gato se mueve con un bucle y gira." in ctx
    assert "BLOQUES CLAVE" in ctx
    # el id se conserva (para bloques_sugeridos) y se traduce a su nombre del catálogo
    assert "eventos_bandera_verde" in ctx
    assert "Al presionar bandera verde" in ctx
    assert "Repetir veces" in ctx


async def test_todos_los_bloques_clave_del_seed_existen_en_el_catalogo(db_session) -> None:
    """Cada código en juegos.bloques_clave del seed debe tener nombre en el catálogo,
    si no render_bloques caería al id crudo. Se valida dinámicamente sobre el seed real."""
    from app.repositories.games import GamesRepository

    data = load_bloques()
    ids = {b["id"] for b in data["bloques"]}
    games = await GamesRepository(db_session).list_active_games()
    faltantes: dict[str, list[str]] = {}
    total_codes = 0
    for game in games:
        for code in parse_block_codes(game.bloques_clave):
            total_codes += 1
            if code not in ids:
                faltantes.setdefault(game.id, []).append(code)
    assert total_codes > 0, "el seed no tiene bloques_clave; ¿se pobló?"
    assert not faltantes, f"bloques_clave sin nombre en el catálogo: {faltantes}"
