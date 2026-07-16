from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.prompts import BIT_SYSTEM_PROMPT
from app.models import Game, GameCategory, GameVersion, Group, Student


async def seed_demo_data(db: AsyncSession) -> None:
    existing_group = await db.scalar(select(Group).where(Group.nombre == "CreaBits Demo"))
    if existing_group is None:
        existing_group = Group(nombre="CreaBits Demo", descripcion="Grupo local para pruebas")
        db.add(existing_group)
        await db.flush()

    students = [
        Student(
            codigo_publico="tigre-azul-7",
            grupo_id=existing_group.id,
            edad=9,
            genero_opcion="prefiero_no_decir",
            experiencia_scratch="un_poco",
            experiencia_ia="ninguna",
        ),
        Student(
            codigo_publico="demo-ia-1",
            grupo_id=existing_group.id,
            edad=10,
            genero_opcion="prefiero_no_decir",
            experiencia_scratch="ninguna",
            experiencia_ia="alguna",
        ),
    ]
    for student in students:
        exists = await db.scalar(select(Student).where(Student.codigo_publico == student.codigo_publico))
        if exists is None:
            db.add(student)

    categories = [
        GameCategory(id="animaciones", nombre="Animaciones", icono="🎬", color_hex="#E91E63", orden=1),
        GameCategory(id="juegos", nombre="Juegos", icono="🎮", color_hex="#7EC242", orden=2),
        GameCategory(id="historias", nombre="Historias", icono="📖", color_hex="#FF8C42", orden=3),
        GameCategory(id="libre", nombre="Libre", icono="✨", color_hex="#9B59B6", orden=4),
    ]
    for category in categories:
        exists = await db.get(GameCategory, category.id)
        if exists is None:
            db.add(category)

    games = [
        Game(
            id="ej_001",
            categoria_id="animaciones",
            titulo="Haz bailar al gato",
            icono="🐱",
            descripcion_corta="Anima un personaje para que baile con música.",
            duracion_estimada_min=20,
            url_video="https://youtu.be/Sf4Dr52UElc",
            descripcion_solucion=(
                "Al presionar la bandera verde, el gato se mueve a la derecha y luego a la izquierda "
                "varias veces usando un bucle, con pequeñas esperas para que el movimiento se vea. "
                "Después gira sobre sí mismo varias veces y vuelve a quedar mirando a la derecha."
            ),
            bloques_clave=(
                '"eventos_bandera_verde","control_repetir_veces","movimiento_cambiar_x",'
                '"control_esperar_segundos","movimiento_girar_derecha_grados","movimiento_apuntar_direccion"'
            ),
        ),
        Game(
            id="ej_002",
            categoria_id="animaciones",
            titulo="Mariposa cambia de disfraz",
            icono="🦋",
            descripcion_corta="Crea una animación suave usando disfraces.",
            duracion_estimada_min=15,
            url_video="https://youtu.be/M1ob_Fa7Fek",
        ),
        Game(
            id="ej_003",
            categoria_id="juegos",
            titulo="Atrapa la estrella",
            icono="⭐",
            descripcion_corta="Mueve un personaje y suma puntos al tocar estrellas.",
            duracion_estimada_min=25,
        ),
        Game(
            id="ej_004",
            categoria_id="juegos",
            titulo="Salta obstáculos",
            icono="🟩",
            descripcion_corta="Programa un salto y evita objetos que se acercan.",
            duracion_estimada_min=30,
        ),
        Game(
            id="ej_005",
            categoria_id="historias",
            titulo="Diálogo entre personajes",
            icono="💬",
            descripcion_corta="Haz que dos personajes conversen en orden.",
            duracion_estimada_min=20,
            url_video="https://youtu.be/4ccq7IIhRcg",
            descripcion_solucion=(
                "Hay dos personajes con scripts separados. El primer personaje arranca con la bandera "
                "verde: saluda con 'decir durante segundos', envía un mensaje (por ejemplo 'mensaje1'), "
                "espera un momento, y luego se presenta con otro 'decir durante segundos'. El segundo "
                "personaje no arranca con bandera verde sino que espera con 'al recibir mensaje1'; cuando "
                "llega ese mensaje, responde el saludo, espera un momento, y luego se presenta también."
            ),
            bloques_clave=(
                '"eventos_bandera_verde","eventos_enviar_mensaje","eventos_al_recibir_mensaje",'
                '"apariencia_decir_segundos","control_esperar_segundos"'
            ),
        ),
        Game(
            id="ej_006",
            categoria_id="historias",
            titulo="Historia con escenarios",
            icono="🏞️",
            descripcion_corta="Cambia fondos para contar una historia.",
            duracion_estimada_min=25,
            url_video="https://www.youtube.com/watch?v=n5P_3XF9dSw",
            descripcion_solucion=(
                "Al presionar la bandera verde, el personaje va contando una historia que se desarrolla "
                "en varios escenarios. En cada escena, primero se cambia el fondo al lugar correspondiente, "
                "luego el personaje dice algo con 'decir durante segundos', después se mueve unos pasos y "
                "cambia al siguiente disfraz para dar sensación de movimiento. El patrón por escena es: "
                "cambiar fondo → decir → mover pasos → siguiente disfraz."
            ),
            bloques_clave=(
                '"eventos_bandera_verde","apariencia_cambiar_fondo","apariencia_decir_segundos",'
                '"movimiento_mover_pasos","apariencia_siguiente_disfraz"'
            ),
        ),
        Game(
            id="proyecto_libre",
            categoria_id="libre",
            titulo="Proyecto libre",
            icono="🚀",
            descripcion_corta="Crea una idea propia con ayuda de Bit.",
            es_proyecto_libre=True,
        ),
    ]
    for game in games:
        exists = await db.get(Game, game.id)
        if exists is None:
            db.add(game)

    await db.flush()

    prompts = {
        "ej_001": "Vamos a hacer que el gato baile. Primero piensa: ¿qué bloque puede iniciar la animación?",
        "ej_002": "Vamos a animar una mariposa cambiando disfraces. ¿Dónde crees que viven los disfraces?",
        "ej_003": "Vamos a crear un juego: tu personaje tiene que atrapar estrellas moviéndose con las flechas.",
        "ej_004": "Vamos a crear un juego de saltar obstáculos. Empezamos por imaginar cómo sube y baja el personaje.",
        "ej_005": "Vamos a crear un diálogo. Primero decide qué personaje habla primero y qué dirá.",
        "ej_006": "Vamos a contar una historia con escenarios. ¿Cuál será el primer lugar de tu historia?",
        "proyecto_libre": "Cuéntame qué quieres crear hoy y lo convertimos en pasos pequeños.",
    }
    for game_id, instruction in prompts.items():
        exists = await db.scalar(
            select(GameVersion).where(GameVersion.juego_id == game_id, GameVersion.version == "v1")
        )
        if exists is None:
            db.add(
                GameVersion(
                    juego_id=game_id,
                    version="v1",
                    instruccion_nino=instruction,
                    objetivos_pedagogicos=["Aprender con preguntas", "Resolver en pasos pequeños"],
                    pistas_progresivas=["Observa los bloques", "Prueba una parte", "Mejora tu proyecto"],
                    criterios_completado=["El estudiante explica su avance", "El proyecto tiene una acción observable"],
                    preguntas_frecuentes_esperadas=["¿Qué bloque uso?", "¿Cómo lo hago funcionar?"],
                    system_prompt=BIT_SYSTEM_PROMPT,
                )
            )

    await db.commit()
