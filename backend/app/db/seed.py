from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, GameCategory, GameVersion, Group, Student

_BASE_SYSTEM_PROMPT = (
    "Eres Bit, tutor de Scratch para niños de 8 a 10 años. "
    "Responde en español simple y animado. "
    "Usa la estrategia Hint Progression: muestra un bloque y pide al niño que prediga qué hace antes de probarlo. "
    "Nunca des la solución completa. Escala las pistas de vaga a concreta. "
    "Una o dos oraciones por turno, máximo un emoji."
)

_GAME_CONFIGS: dict[str, dict] = {
    "ej_001": {
        "instruccion_nino": "¡Vamos a hacer bailar al gato! Primero piensa: ¿qué bloque hace que el programa empiece?",
        "objetivos": ["Usar evento bandera verde", "Mover y girar el personaje", "Usar repetición para animar"],
        "pistas": [
            "Fíjate en la categoría Eventos para arrancar el programa.",
            "En Movimiento hay bloques que giran y mueven al gato.",
            "Para que baile de verdad, usa Repetir de la categoría Control.",
        ],
        "preguntas_esperadas": ["¿Qué bloque inicio?", "¿Cómo hago que se mueva?", "¿Cómo lo repito?"],
        "system_prompt_extra": (
            "Este ejercicio enseña: eventos (bandera verde), movimiento (mover pasos, girar), control (repetir veces). "
            "Bloques clave: eventos_bandera_verde, movimiento_mover_pasos, movimiento_girar_derecha_grados, control_repetir_veces, control_por_siempre."
        ),
    },
    "ej_002": {
        "instruccion_nino": "¡Vamos a animar una mariposa cambiando sus disfraces! ¿Dónde crees que están los disfraces?",
        "objetivos": ["Usar disfraces para animar", "Agregar pausas para suavizar la animación"],
        "pistas": [
            "Los disfraces viven en la categoría Apariencia.",
            "Para que la animación se vea bien, agrega un Esperar entre cambios de disfraz.",
            "Prueba: siguiente disfraz → esperar → siguiente disfraz. ¿Qué pasa?",
        ],
        "preguntas_esperadas": ["¿Dónde están los disfraces?", "¿Cómo la animo?", "¿Por qué se ve raro?"],
        "system_prompt_extra": (
            "Este ejercicio enseña: apariencia (siguiente disfraz), control (esperar, por siempre). "
            "Bloques clave: apariencia_siguiente_disfraz, apariencia_cambiar_disfraz, control_esperar_segundos, control_por_siempre, eventos_bandera_verde."
        ),
    },
    "ej_003": {
        "instruccion_nino": "¡Vamos a crear un juego donde tu personaje atrapa estrellas! ¿Cómo harías que se mueva con las flechas?",
        "objetivos": ["Controlar personaje con teclas", "Detectar colisión con objeto", "Usar variable para puntaje"],
        "pistas": [
            "Para las flechas, busca en Eventos un bloque que reaccione a teclas.",
            "Para detectar si tocas la estrella, mira la categoría Sensores.",
            "Los puntos se guardan en una Variable que va subiendo cuando tocas la estrella.",
        ],
        "preguntas_esperadas": ["¿Cómo me muevo con flechas?", "¿Cómo cuento puntos?", "¿Cómo sé si toco la estrella?"],
        "system_prompt_extra": (
            "Este ejercicio enseña: eventos (tecla presionada), movimiento (cambiar x/y), sensores (tocando), variables (cambiar). "
            "Bloques clave: eventos_tecla_presionada, movimiento_cambiar_x, movimiento_cambiar_y, sensores_tocando, variables_boton_crear, variables_cambiar, control_por_siempre."
        ),
    },
    "ej_004": {
        "instruccion_nino": "¡Vamos a crear un juego de saltar obstáculos! Primero imagina: ¿cómo sube y baja el personaje al saltar?",
        "objetivos": ["Programar un salto con gravedad simple", "Mover obstáculos automáticamente", "Detectar colisión para terminar el juego"],
        "pistas": [
            "Para saltar, la posición Y del personaje tiene que subir y luego bajar.",
            "Los obstáculos se mueven solos usando Por Siempre y cambiando su posición X.",
            "Para detectar si chocas, usa el bloque Tocando del sensor.",
        ],
        "preguntas_esperadas": ["¿Cómo salto?", "¿Cómo muevo el obstáculo?", "¿Cómo sé si perdí?"],
        "system_prompt_extra": (
            "Este ejercicio enseña: movimiento (cambiar y, fijar y), control (por siempre, si entonces), sensores (tocando). "
            "Bloques clave: movimiento_cambiar_y, movimiento_fijar_y, control_por_siempre, control_si_entonces, sensores_tocando, eventos_tecla_presionada."
        ),
    },
    "ej_005": {
        "instruccion_nino": "¡Vamos a crear un diálogo entre dos personajes! Primero decide qué dirá el primero y qué dirá el segundo.",
        "objetivos": ["Hacer hablar personajes en orden", "Usar mensajes para coordinar personajes"],
        "pistas": [
            "Para que el personaje hable, busca en Apariencia un bloque que muestre texto.",
            "Para que hablen en orden, el primero debe enviar un mensaje cuando termine.",
            "El segundo personaje empieza cuando recibe ese mensaje.",
        ],
        "preguntas_esperadas": ["¿Cómo hablo?", "¿Cómo hablan en orden?", "¿Qué es un mensaje?"],
        "system_prompt_extra": (
            "Este ejercicio enseña: apariencia (decir durante segundos), eventos (enviar mensaje, al recibir mensaje). "
            "Bloques clave: apariencia_decir_segundos, apariencia_decir, eventos_enviar_mensaje, eventos_enviar_mensaje_y_esperar, eventos_al_recibir_mensaje."
        ),
    },
    "ej_006": {
        "instruccion_nino": "¡Vamos a contar una historia con distintos escenarios! ¿Cuál será el primer lugar de tu historia?",
        "objetivos": ["Cambiar fondos para narrar escenas", "Coordinar personajes y fondos con mensajes"],
        "pistas": [
            "Para cambiar la escena, busca en Apariencia el bloque que cambia el fondo.",
            "Cuando el fondo cambie, el personaje puede decir algo para continuar la historia.",
            "Usa mensajes para que el cambio de escena active acciones de los personajes.",
        ],
        "preguntas_esperadas": ["¿Cómo cambio el fondo?", "¿Cómo hago que pase algo al cambiar?"],
        "system_prompt_extra": (
            "Este ejercicio enseña: apariencia (cambiar fondo), eventos (enviar mensaje, al recibir), apariencia (decir). "
            "Bloques clave: apariencia_cambiar_fondo, apariencia_decir_segundos, eventos_enviar_mensaje, eventos_al_recibir_mensaje."
        ),
    },
    "proyecto_libre": {
        "instruccion_nino": "¡Cuéntame qué quieres crear hoy y lo convertimos en pasos pequeños!",
        "objetivos": ["Explorar creativamente Scratch", "Dividir ideas en pasos concretos"],
        "pistas": [
            "Primero decide: ¿qué hace tu personaje principal?",
            "Piensa en tres partes: cómo empieza, qué pasa en el medio, cómo termina.",
            "Elige un bloque de Eventos para arrancar tu proyecto y pruébalo.",
        ],
        "preguntas_esperadas": ["¿Cómo empiezo?", "¿Qué bloque uso para mi idea?"],
        "system_prompt_extra": (
            "Proyecto libre: adapta las sugerencias a la idea del niño. "
            "Ayuda a estructurar: personaje → acción → evento de inicio. "
            "Sugiere bloques solo cuando el niño tenga una idea concreta."
        ),
    },
}


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
        Student(
            codigo_publico="leon-rojo-3",
            grupo_id=existing_group.id,
            edad=8,
            genero_opcion="prefiero_no_decir",
            experiencia_scratch="ninguna",
            experiencia_ia="ninguna",
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
            descripcion_solucion=(
                "Al presionar la bandera verde, la mariposa cambia de disfraz una y otra vez dentro "
                "de un bucle, dejando una pequeña espera entre cada cambio para que la animación se "
                "vea suave y continua."
            ),
            bloques_clave=(
                '"eventos_bandera_verde","control_por_siempre","apariencia_siguiente_disfraz",'
                '"control_esperar_segundos"'
            ),
        ),
        Game(
            id="ej_003",
            categoria_id="juegos",
            titulo="Atrapa la estrella",
            icono="⭐",
            descripcion_corta="Mueve un personaje y suma puntos al tocar estrellas.",
            duracion_estimada_min=25,
            descripcion_solucion=(
                "Con la bandera verde arranca el juego. El personaje se mueve con las teclas de flecha "
                "cambiando su posición x e y. En un bucle 'por siempre' se revisa si toca la estrella; "
                "cuando la toca, una variable de puntaje sube."
            ),
            bloques_clave=(
                '"eventos_bandera_verde","eventos_tecla_presionada","movimiento_cambiar_x",'
                '"movimiento_cambiar_y","control_por_siempre","sensores_tocando",'
                '"variables_boton_crear","variables_cambiar"'
            ),
        ),
        Game(
            id="ej_004",
            categoria_id="juegos",
            titulo="Salta obstáculos",
            icono="🟩",
            descripcion_corta="Programa un salto y evita objetos que se acercan.",
            duracion_estimada_min=30,
            descripcion_solucion=(
                "Al presionar la bandera verde, el personaje salta subiendo y luego bajando su posición "
                "y. Los obstáculos se mueven solos con un bucle 'por siempre'; con un 'si entonces' se "
                "revisa si el personaje toca un obstáculo para reaccionar (por ejemplo, terminar el juego)."
            ),
            bloques_clave=(
                '"eventos_bandera_verde","eventos_tecla_presionada","movimiento_cambiar_y",'
                '"movimiento_fijar_y","control_por_siempre","control_si_entonces","sensores_tocando"'
            ),
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

    for game_id, cfg in _GAME_CONFIGS.items():
        exists = await db.scalar(
            select(GameVersion).where(GameVersion.juego_id == game_id, GameVersion.version == "v1")
        )
        if exists is None:
            db.add(
                GameVersion(
                    juego_id=game_id,
                    version="v1",
                    instruccion_nino=cfg["instruccion_nino"],
                    objetivos_pedagogicos=cfg["objetivos"],
                    pistas_progresivas=cfg["pistas"],
                    criterios_completado=[
                        "El estudiante explica su avance con sus propias palabras",
                        "El proyecto tiene al menos una acción visible al ejecutarse",
                    ],
                    preguntas_frecuentes_esperadas=cfg["preguntas_esperadas"],
                    system_prompt=_BASE_SYSTEM_PROMPT + "\n\n" + cfg["system_prompt_extra"],
                )
            )

    await db.commit()
