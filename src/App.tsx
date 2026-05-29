import React, { useState, useEffect, useRef } from 'react';
import { supabase } from './supabaseClient';

type SessionData = {
  usuario_id: string;
  codigo_nemonico: string;
  sesion_id: string;
  conversacion_id: string;
};

const BitRobot = ({ size = 120, mood = "happy", animated = true }: any) => {
  const eyeY = mood === "thinking" ? 35 : 38;
  const mouthPath = mood === "happy" ? "M 35 55 Q 50 65 65 55" : mood === "thinking" ? "M 38 58 L 62 58" : "M 35 60 Q 50 50 65 60";
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className={animated ? "bit-bounce" : ""}>
      <line x1="50" y1="8" x2="50" y2="18" stroke="#9B59B6" strokeWidth="2.5" strokeLinecap="round"/>
      <circle cx="50" cy="6" r="3.5" fill="#E91E63"/>
      <rect x="20" y="18" width="60" height="50" rx="14" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="2.5"/>
      <ellipse cx="30" cy="28" rx="8" ry="4" fill="#fff" opacity="0.25"/>
      <circle cx="36" cy={eyeY} r="6" fill="#fff"/>
      <circle cx="64" cy={eyeY} r="6" fill="#fff"/>
      <circle cx="37" cy={eyeY + 1} r="3" fill="#1a1a1a"/>
      <circle cx="65" cy={eyeY + 1} r="3" fill="#1a1a1a"/>
      <circle cx="38" cy={eyeY} r="1" fill="#fff"/>
      <circle cx="66" cy={eyeY} r="1" fill="#fff"/>
      <circle cx="26" cy="50" r="4" fill="#FF8C42" opacity="0.5"/>
      <circle cx="74" cy="50" r="4" fill="#FF8C42" opacity="0.5"/>
      <path d={mouthPath} stroke="#1a1a1a" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
      <rect x="30" y="68" width="40" height="22" rx="6" fill="#F4C842" stroke="#1a1a1a" strokeWidth="2.5"/>
      <circle cx="40" cy="79" r="2" fill="#E74C3C"/>
      <circle cx="50" cy="79" r="2" fill="#7EC242"/>
      <circle cx="60" cy="79" r="2" fill="#9B59B6"/>
      <rect x="12" y="72" width="8" height="14" rx="3" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="2"/>
      <rect x="80" y="72" width="8" height="14" rx="3" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="2"/>
    </svg>
  );
};

const PreviewEjercicio = ({ ejercicioId, color = "#2E9DF7" }: any) => {
  const previews: any = {
    ej_001: (
      <svg viewBox="0 0 100 60" className="w-full h-24">
        <rect width="100" height="60" fill="#FFF5E1"/>
        <circle cx="35" cy="35" r="14" fill="#FF8C42"/>
        <polygon points="25,25 28,18 32,25" fill="#FF8C42"/>
        <polygon points="38,25 42,18 45,25" fill="#FF8C42"/>
        <circle cx="32" cy="33" r="2" fill="#1a1a1a"/>
        <circle cx="38" cy="33" r="2" fill="#1a1a1a"/>
        <path d="M 33 38 Q 35 40 37 38" stroke="#1a1a1a" strokeWidth="1" fill="none"/>
        <text x="55" y="32" fontSize="14" fill="#E91E63">♪</text>
        <text x="68" y="40" fontSize="11" fill="#9B59B6">♫</text>
        <text x="78" y="28" fontSize="14" fill="#E91E63">♪</text>
      </svg>
    ),
    ej_002: (
      <svg viewBox="0 0 100 60" className="w-full h-24">
        <rect width="100" height="60" fill="#E8F5E9"/>
        <ellipse cx="40" cy="30" rx="10" ry="14" fill="#9B59B6" transform="rotate(-20 40 30)"/>
        <ellipse cx="60" cy="30" rx="10" ry="14" fill="#E91E63" transform="rotate(20 60 30)"/>
        <rect x="48" y="22" width="4" height="18" rx="2" fill="#1a1a1a"/>
        <line x1="50" y1="22" x2="46" y2="16" stroke="#1a1a1a" strokeWidth="1.5"/>
        <line x1="50" y1="22" x2="54" y2="16" stroke="#1a1a1a" strokeWidth="1.5"/>
        <circle cx="46" cy="15" r="1.5" fill="#1a1a1a"/>
        <circle cx="54" cy="15" r="1.5" fill="#1a1a1a"/>
      </svg>
    ),
    ej_003: (
      <svg viewBox="0 0 100 60" className="w-full h-24">
        <rect width="100" height="60" fill="#FFF9C4"/>
        <polygon points="20,15 23,22 30,22 24,27 27,34 20,30 13,34 16,27 10,22 17,22" fill="#F4C842" stroke="#1a1a1a" strokeWidth="1"/>
        <polygon points="70,40 73,47 80,47 74,52 77,59 70,55 63,59 66,52 60,47 67,47" fill="#F4C842" stroke="#1a1a1a" strokeWidth="1"/>
        <rect x="40" y="30" width="20" height="20" rx="4" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="1.5"/>
        <circle cx="46" cy="38" r="2" fill="#fff"/>
        <circle cx="54" cy="38" r="2" fill="#fff"/>
        <path d="M 45 44 Q 50 47 55 44" stroke="#fff" strokeWidth="1.5" fill="none"/>
      </svg>
    ),
    ej_004: (
      <svg viewBox="0 0 100 60" className="w-full h-24">
        <rect width="100" height="60" fill="#E3F2FD"/>
        <line x1="0" y1="50" x2="100" y2="50" stroke="#1a1a1a" strokeWidth="2"/>
        <circle cx="25" cy="35" r="8" fill="#7EC242" stroke="#1a1a1a" strokeWidth="1.5"/>
        <circle cx="22" cy="33" r="1.5" fill="#1a1a1a"/>
        <circle cx="28" cy="33" r="1.5" fill="#1a1a1a"/>
        <rect x="55" y="38" width="12" height="12" fill="#E74C3C" stroke="#1a1a1a" strokeWidth="1.5"/>
        <rect x="78" y="38" width="12" height="12" fill="#E74C3C" stroke="#1a1a1a" strokeWidth="1.5"/>
        <path d="M 25 28 L 25 22 M 22 25 L 28 25" stroke="#9B59B6" strokeWidth="2" strokeLinecap="round"/>
      </svg>
    ),
    ej_005: (
      <svg viewBox="0 0 100 60" className="w-full h-24">
        <rect width="100" height="60" fill="#FFF3E0"/>
        <circle cx="30" cy="35" r="12" fill="#2E9DF7" stroke="#1a1a1a" strokeWidth="1.5"/>
        <circle cx="27" cy="33" r="1.5" fill="#1a1a1a"/>
        <circle cx="33" cy="33" r="1.5" fill="#1a1a1a"/>
        <path d="M 27 38 Q 30 40 33 38" stroke="#1a1a1a" strokeWidth="1" fill="none"/>
        <circle cx="70" cy="35" r="12" fill="#E91E63" stroke="#1a1a1a" strokeWidth="1.5"/>
        <circle cx="67" cy="33" r="1.5" fill="#1a1a1a"/>
        <circle cx="73" cy="33" r="1.5" fill="#1a1a1a"/>
        <path d="M 67 38 Q 70 40 73 38" stroke="#1a1a1a" strokeWidth="1" fill="none"/>
        <ellipse cx="50" cy="15" rx="14" ry="7" fill="#fff" stroke="#1a1a1a" strokeWidth="1"/>
        <text x="44" y="18" fontSize="8" fill="#1a1a1a">¡Hola!</text>
      </svg>
    ),
    ej_006: (
      <svg viewBox="0 0 100 60" className="w-full h-24">
        <rect x="0" y="0" width="50" height="60" fill="#7EC242"/>
        <rect x="50" y="0" width="50" height="60" fill="#FFE082"/>
        <circle cx="15" cy="15" r="6" fill="#F4C842"/>
        <polygon points="10,50 18,30 26,50" fill="#1B5E20"/>
        <polygon points="22,50 30,28 38,50" fill="#2E7D32"/>
        <rect x="65" y="35" width="20" height="20" fill="#FF8C42" stroke="#1a1a1a" strokeWidth="1"/>
        <polygon points="65,35 75,25 85,35" fill="#E74C3C"/>
        <line x1="50" y1="0" x2="50" y2="60" stroke="#1a1a1a" strokeWidth="2" strokeDasharray="3,3"/>
      </svg>
    ),
    proyecto_libre: (
      <svg viewBox="0 0 100 60" className="w-full h-24">
        <rect width="100" height="60" fill="#F3E5F5"/>
        <text x="20" y="35" fontSize="24">✨</text>
        <text x="45" y="42" fontSize="20">🎨</text>
        <text x="70" y="30" fontSize="22">🚀</text>
        <text x="15" y="50" fontSize="16">🎵</text>
        <text x="78" y="50" fontSize="18">💡</text>
      </svg>
    )
  };
  return previews[ejercicioId] || (
    <svg viewBox="0 0 100 60" className="w-full h-24"><rect width="100" height="60" fill={color}/></svg>
  );
};

const Header = ({ codigo, onExit, showExit = true, ejercicio, onVolver, mostrarVolver = false }: any) => (
  <div className="bg-[#1a1a1a] text-white px-6 py-4 flex items-center justify-between shadow-lg">
    <div className="flex items-center gap-3">
      {mostrarVolver && (
        <button onClick={onVolver} className="text-white/70 hover:text-white text-2xl mr-2" title="Volver">←</button>
      )}
      <div className="flex items-center">
        <span style={{color: '#2E9DF7'}} className="font-black text-2xl">C</span>
        <span style={{color: '#E74C3C'}} className="font-black text-2xl">r</span>
        <span style={{color: '#F4C842'}} className="font-black text-2xl">e</span>
        <span style={{color: '#7EC242'}} className="font-black text-2xl">a</span>
        <span style={{color: '#E91E63'}} className="font-black text-2xl">B</span>
        <span style={{color: '#FF8C42'}} className="font-black text-2xl">i</span>
        <span style={{color: '#FF8C42'}} className="font-black text-2xl">T</span>
        <span style={{color: '#9B59B6'}} className="font-black text-2xl">s</span>
      </div>
      {ejercicio && (
        <div className="hidden sm:block ml-4 px-3 py-1 bg-white/10 rounded-full text-sm">
          {ejercicio.icono} {ejercicio.titulo}
        </div>
      )}
    </div>
    <div className="flex items-center gap-3">
      {codigo && (
        <div className="hidden sm:block text-sm bg-white/10 px-3 py-1 rounded-full">🎫 {codigo}</div>
      )}
      {showExit && (
        <button onClick={onExit} className="text-sm bg-white/10 hover:bg-white/20 px-3 py-2 rounded-lg transition">Salir</button>
      )}
    </div>
  </div>
);

const PantallaBienvenida = ({ onEntrar }: any) => {
  const [codigo, setCodigo] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const handleEntrar = async () => {
    const c = codigo.trim().toLowerCase();
    if (!c) { setError("Escribe tu código para entrar"); return; }
    setCargando(true);

    const { data, error: dbError } = await supabase
      .from('usuarios')
      .select('id')
      .eq('codigo_nemonico', c)
      .single();

    setCargando(false);

    if (data) onEntrar(c, data.id);
    else setError("No reconozco ese código. Pídele ayuda a tu profe.");
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header showExit={false} />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full fade-in">
          <div className="flex justify-center mb-4"><BitRobot size={140} /></div>
          <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
            ¡Hola! Soy <span style={{color: '#2E9DF7'}}>Bit</span> 👋
          </h1>
          <p className="text-center text-gray-600 mb-6">Tu ayudante de Scratch. ¿Empezamos?</p>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Escribe tu código:</label>
          <input
            type="text" value={codigo}
            onChange={(e) => { setCodigo(e.target.value); setError(""); }}
            onKeyDown={(e) => e.key === "Enter" && handleEntrar()}
            placeholder="tigre-azul-7"
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-lg focus:border-[#2E9DF7] focus:outline-none transition text-center"
          />
          {error && <p className="text-[#E74C3C] text-sm mt-2 text-center fade-in">{error}</p>}
          <button onClick={handleEntrar} disabled={cargando} className="w-full mt-6 py-4 bg-[#2E9DF7] hover:bg-[#1a8de8] disabled:bg-gray-400 text-white font-bold text-lg rounded-xl shadow-md hover:shadow-lg transition transform hover:scale-[1.02]">
            {cargando ? "Buscando..." : "Entrar →"}
          </button>
          <p className="text-xs text-gray-400 text-center mt-6">¿No tienes código? Pídele a tu profe.</p>
        </div>
      </div>
    </div>
  );
};

const PantallaAsentimiento = ({ session, onAceptar, onRechazar }: any) => {
  const [cargando, setCargando] = useState(false);

  const handleAceptar = async () => {
    setCargando(true);
    const { data, error } = await supabase
      .from('sesiones')
      .insert([{ usuario_id: session.usuario_id, asentimiento_aceptado: true }])
      .select().single();
    setCargando(false);
    if (data) onAceptar(data.id);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header codigo={session.codigo_nemonico} showExit={false} />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-2xl w-full fade-in">
          <div className="flex justify-center mb-4"><BitRobot size={120} /></div>
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
            ¡Qué bueno verte, <span style={{color: '#2E9DF7'}}>{session.codigo_nemonico}</span>!
          </h2>
          <p className="text-center text-gray-500 mb-6">Antes de empezar, quiero contarte algo importante:</p>
          <div className="space-y-4 text-gray-700 text-lg">
            <div className="flex gap-3 items-start"><div className="text-2xl">🤖</div><p>Yo soy un <strong>programa de computadora</strong>, no una persona real.</p></div>
            <div className="flex gap-3 items-start"><div className="text-2xl">💬</div><p>Vamos a conversar para que aprendas Scratch.</p></div>
            <div className="flex gap-3 items-start"><div className="text-2xl">👀</div><p>Lo que escribamos lo va a <strong>leer tu profe</strong>.</p></div>
            <div className="flex gap-3 items-start"><div className="text-2xl">🚪</div><p>Si no quieres seguir, dile a tu profe o aprieta <strong>"Salir"</strong>.</p></div>
          </div>
          <p className="text-center mt-8 text-gray-800 font-semibold">¿Quieres empezar?</p>
          <div className="grid grid-cols-2 gap-3 mt-4">
            <button onClick={onRechazar} className="py-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl transition">No, mejor no</button>
            <button onClick={handleAceptar} disabled={cargando} className="py-4 bg-[#7EC242] hover:bg-[#6ab038] disabled:bg-gray-400 text-white font-bold rounded-xl shadow-md transition transform hover:scale-[1.02]">
              {cargando ? "Creando sesión..." : "¡Sí, vamos! ✨"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const PantallaSeleccion = ({ session, onSeleccionar, onSalir }: any) => {
  const [categoriaActiva, setCategoriaActiva] = useState("todos");
  const [cargando, setCargando] = useState(false);
  const [ejerciciosDb, setEjerciciosDb] = useState<any[]>([]);
  const [categoriasDb, setCategoriasDb] = useState<any[]>([]);
  const [cargandoEjercicios, setCargandoEjercicios] = useState(true);

  useEffect(() => {
    const fetchEjercicios = async () => {
      try {
        const { data: ejercicios, error } = await supabase
          .from('ejercicios')
          .select('*');

        if (error) {
          console.error("Error al cargar ejercicios de Supabase:", error);
          setCargandoEjercicios(false);
          return;
        }

        if (ejercicios) {
          setEjerciciosDb(ejercicios);
          
          const catsUnicas = Array.from(new Set(ejercicios.map(e => e.categoria))).filter(c => c);
          
          const categoriasMap = catsUnicas.map(cat => ({
            id: cat,
            nombre: cat === 'animaciones' ? 'Animaciones' : 
                    cat === 'juegos' ? 'Juegos' : 
                    cat === 'historias' ? 'Historias' : cat,
            icono: cat === 'animaciones' ? '🎬' : 
                   cat === 'juegos' ? '🎮' : 
                   cat === 'historias' ? '📖' : '✨',
            color: cat === 'animaciones' ? '#E91E63' : 
                   cat === 'juegos' ? '#7EC242' : 
                   cat === 'historias' ? '#FF8C42' : '#9B59B6'
          }));
          
          setCategoriasDb(categoriasMap);
        }
      } catch (err) {
        console.error("Error de red al cargar ejercicios:", err);
      } finally {
        setCargandoEjercicios(false);
      }
    };

    fetchEjercicios();
  }, []);

  const categoriasFiltro = [
    { id: "todos", nombre: "Todos", icono: "🌟", color: "#2E9DF7" },
    ...categoriasDb
  ];

  const ejerciciosNormales = ejerciciosDb.filter(e => e.id !== 'proyecto_libre');
  const proyectoLibre = ejerciciosDb.find(e => e.id === 'proyecto_libre');

  const ejerciciosFiltrados = categoriaActiva === "todos"
    ? ejerciciosNormales
    : ejerciciosNormales.filter((e: any) => e.categoria === categoriaActiva);

  const getCategoria = (idCat: string) => categoriasDb.find((c: any) => c.id === idCat);

  const handleSeleccion = async (ej: any) => {
    setCargando(true);
    
    try {
      const { data, error } = await supabase
        .from('conversaciones')
        .insert([{ 
          sesion_id: session.sesion_id, 
          usuario_id: session.usuario_id, 
          ejercicio_id: ej.id 
        }])
        .select().single();
      
      setCargando(false);

      if (error) {
        console.error("Error de Supabase al crear conversación:", error.message);
        onSeleccionar(ej, `dummy-conv-${Date.now()}`);
      } else if (data) {
        onSeleccionar(ej, data.id);
      }
    } catch (err) {
      setCargando(false);
      console.error("Error de red o ejecución:", err);
      onSeleccionar(ej, `dummy-conv-${Date.now()}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header codigo={session.codigo_nemonico} onExit={onSalir} />
      <div className="flex-1 p-6 max-w-6xl mx-auto w-full">
        <div className="text-center mb-6 fade-in">
          <div className="flex justify-center mb-3"><BitRobot size={80} /></div>
          <h2 className="text-3xl font-bold text-gray-800">¿Qué quieres hacer hoy, <span style={{color: '#2E9DF7'}}>{session.codigo_nemonico}</span>?</h2>
          <p className="text-gray-600 mt-2">Escoge un ejercicio o crea algo libre ✨</p>
        </div>

        {cargandoEjercicios ? (
          <div className="flex justify-center items-center py-20">
            <div className="text-xl font-bold text-gray-500 animate-pulse">Cargando ejercicios...</div>
          </div>
        ) : (
          <>
            {/* Filtros de categoría */}
            <div className="flex flex-wrap gap-2 justify-center mb-6">
              {categoriasFiltro.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setCategoriaActiva(cat.id)}
                  className={`px-4 py-2 rounded-full font-semibold transition ${
                    categoriaActiva === cat.id ? "text-white shadow-md" : "bg-white text-gray-700 border-2 border-gray-200 hover:border-gray-300"
                  }`}
                  style={categoriaActiva === cat.id ? { backgroundColor: cat.color } : {}}
                >
                  {cat.icono} {cat.nombre}
                </button>
              ))}
            </div>

            {/* Grid de ejercicios */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {ejerciciosFiltrados.map((ej: any) => {
                const cat = getCategoria(ej.categoria);
                return (
                  <button
                    key={ej.id} disabled={cargando}
                    onClick={() => handleSeleccion(ej)}
                    className={`card-hover bg-white rounded-2xl overflow-hidden shadow text-left fade-in border-2 border-transparent ${cargando ? 'opacity-50 cursor-wait' : ''}`}
                    style={{ borderColor: cat?.color + "33" }}
                  >
                    <PreviewEjercicio ejercicioId={ej.id} color={cat?.color || "#2E9DF7"} />
                    <div className="p-4">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{ej.icono}</span>
                        {cat && (
                          <span className="text-xs px-2 py-1 rounded-full font-semibold" style={{ backgroundColor: cat.color + "22", color: cat.color }}>
                            {cat.icono} {cat.nombre}
                          </span>
                        )}
                      </div>
                      <h3 className="font-bold text-gray-800 text-lg mb-1">{ej.titulo}</h3>
                      <p className="text-sm text-gray-600 mb-3">{ej.descripcion_corta}</p>
                      
                      {/* Si tu DB guardó los conceptos como array */}
                      {ej.conceptos && Array.isArray(ej.conceptos) && (
                        <div className="flex flex-wrap gap-1 mb-2">
                          {ej.conceptos.slice(0, 3).map((c: string) => (
                            <span key={c} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{c}</span>
                          ))}
                        </div>
                      )}
                      
                      {ej.duracion_estimada_min && (
                        <div className="text-xs text-gray-500 flex items-center gap-1">
                          ⏱️ ~{ej.duracion_estimada_min} min
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}

              {/* Tarjeta especial: Proyecto Libre */}
              {(categoriaActiva === "todos" && proyectoLibre) && (
                <button
                  disabled={cargando}
                  onClick={() => handleSeleccion(proyectoLibre)}
                  className={`card-hover rounded-2xl overflow-hidden shadow text-left fade-in border-2 ${cargando ? 'opacity-50 cursor-wait' : ''}`}
                  style={{ borderColor: proyectoLibre.color_acento || "#9B59B6", background: "linear-gradient(135deg, #F3E5F5 0%, #fff 100%)" }}
                >
                  <PreviewEjercicio ejercicioId="proyecto_libre" />
                  <div className="p-4">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-2xl">{proyectoLibre.icono}</span>
                      <span className="text-xs px-2 py-1 rounded-full font-semibold text-white" style={{ backgroundColor: proyectoLibre.color_acento || "#9B59B6" }}>
                        Libre
                      </span>
                    </div>
                    <h3 className="font-bold text-gray-800 text-lg mb-1">{proyectoLibre.titulo}</h3>
                    <p className="text-sm text-gray-600 mb-3">{proyectoLibre.descripcion_corta}</p>
                    <div className="text-xs text-gray-500">✨ Tú decides qué crear</div>
                  </div>
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

const PantallaChat = ({ session, ejercicio, onSalir, onVolverASeleccion }: any) => {
  const [mensajes, setMensajes] = useState([
    { rol: "tutor", contenido: ejercicio.instruccion_nino, timestamp: new Date().toISOString() }
  ]);
  const [input, setInput] = useState("");
  const [escribiendo, setEscribiendo] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [mensajes, escribiendo]);

  const respuestasPorEjercicio: any = {
    ej_001: ["¡Buena pregunta! 🤔 Mira la categoría azul 'Movimiento'. ¿Qué bloque crees que mueve al gato?", "Casi lo tienes. ¿Probaste con 'mover ___ pasos'?", "Para bailar sin parar, necesita repetir. ¿Sabes qué bloque hace eso?"],
    ej_002: ["¡La mariposa ya tiene dos disfraces! ¿Cómo crees que cambiamos entre ellos?", "Busca en 'Apariencia' (morado). ¿Ves algún bloque de disfraz?", "Para que se vea suave, prueba agregar un 'esperar' chiquito entre cambios."],
    ej_003: ["¡Vamos paso a paso! Primero el movimiento: ¿qué bloque se activa al apretar una flecha?", "Para saber si tocó la estrella, mira en 'Sensores' (azul claro). ¿Ves 'tocando ___?'", "Para contar puntos necesitamos una variable. ¿Has creado una antes?"],
    ej_004: ["¡Empecemos por el salto! ¿Qué crees que pasa con la posición Y cuando alguien salta?", "Los obstáculos vienen de la derecha. ¿Cómo los movemos hacia la izquierda?", "¡Wow, estás pensando en clones! Eso es muy avanzado, te ayudo."],
    ej_005: ["¡Qué buena idea! Primero, ¿cómo hacemos que un personaje diga algo?", "Para que el otro responda en orden, usamos mensajes. ¿Has visto 'enviar a todos'?", "El truco: cuando uno termina, envía un mensaje, y el otro lo escucha."],
    ej_006: ["¡Suena divertido! Primero necesitamos varios fondos. ¿Sabes dónde se agregan?", "Para cambiar de fondo, busca 'cambiar fondo a ___' en Apariencia.", "Los personajes pueden actuar según el fondo con 'cuando el fondo cambia a ___'."],
    proyecto_libre: ["¡Qué emocionante! 🚀 Cuéntame: ¿qué quieres crear hoy?", "¡Buena idea! Vamos a planearla en pasos pequeños. ¿Cuál parte hacemos primero?", "Eso suena divertido. ¿Quieres empezar por el personaje o por el escenario?", "Si te sirve, te doy 3 ideas: una historia, un mini-juego, o una animación. ¿Cuál te llama más?"]
  };

  const enviarMensaje = async () => {
    const texto = input.trim();
    if (!texto) return;

    const ordenNino = mensajes.length + 1;
    setMensajes(prev => [...prev, { rol: "niño", contenido: texto, timestamp: new Date().toISOString() }]);
    setInput("");
    setEscribiendo(true);

    await supabase.from('mensajes').insert([{ 
      conversacion_id: session.conversacion_id, 
      orden: ordenNino, rol: "niño", contenido: texto, version_system_prompt: "dummy-v1" 
    }]);

    setTimeout(async () => {
      const opciones = respuestasPorEjercicio[ejercicio.id] || respuestasPorEjercicio.proyecto_libre;
      const respuesta = opciones[Math.floor(Math.random() * opciones.length)];
      
      setMensajes(prev => [...prev, { rol: "tutor", contenido: respuesta, timestamp: new Date().toISOString() }]);
      setEscribiendo(false);

      await supabase.from('mensajes').insert([{ 
        conversacion_id: session.conversacion_id, 
        orden: ordenNino + 1, rol: "tutor", contenido: respuesta, version_system_prompt: "dummy-v1" 
      }]);
    }, 1200 + Math.random() * 800);
  };

  return (
    <div className="min-h-screen flex flex-col h-screen">
      <Header codigo={session.codigo_nemonico} ejercicio={ejercicio} onExit={onSalir} mostrarVolver={true} onVolver={onVolverASeleccion} />
      <div className="flex-1 overflow-y-auto chat-messages px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {mensajes.map((msg, i) => (
            <div key={i} className={`flex gap-3 fade-in ${msg.rol === "niño" ? "justify-end" : "justify-start"}`}>
              {msg.rol === "tutor" && <div className="flex-shrink-0"><BitRobot size={48} animated={false} /></div>}
              <div className={`max-w-[75%] px-5 py-3 rounded-2xl shadow-sm ${msg.rol === "niño" ? "bg-[#FF8C42] text-white rounded-br-sm" : "bg-white border-2 border-gray-100 text-gray-800 rounded-bl-sm"}`}>
                <p className="text-base leading-relaxed">{msg.contenido}</p>
              </div>
              {msg.rol === "niño" && <div className="flex-shrink-0 w-12 h-12 rounded-full bg-[#FF8C42] flex items-center justify-center text-white font-bold text-lg shadow">{session.codigo_nemonico.charAt(0).toUpperCase()}</div>}
            </div>
          ))}
          {escribiendo && (
            <div className="flex gap-3 justify-start fade-in">
              <div className="flex-shrink-0"><BitRobot size={48} animated={false} mood="thinking" /></div>
              <div className="bg-white border-2 border-gray-100 px-5 py-4 rounded-2xl rounded-bl-sm">
                <div className="flex gap-1.5">
                  <div className="typing-dot w-2 h-2 bg-[#2E9DF7] rounded-full"></div>
                  <div className="typing-dot w-2 h-2 bg-[#2E9DF7] rounded-full"></div>
                  <div className="typing-dot w-2 h-2 bg-[#2E9DF7] rounded-full"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      <div className="bg-white border-t-2 border-gray-100 p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text" value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && enviarMensaje()}
            placeholder="Escribe tu pregunta a Bit..."
            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#2E9DF7] focus:outline-none transition"
          />
          <button onClick={enviarMensaje} disabled={!input.trim() || escribiendo} className="px-6 py-3 bg-[#2E9DF7] hover:bg-[#1a8de8] disabled:bg-gray-300 text-white font-bold rounded-xl shadow-md transition transform hover:scale-[1.02] disabled:transform-none">
            Enviar
          </button>
        </div>
        <div className="max-w-3xl mx-auto mt-2 flex justify-center gap-4">
          <button onClick={onVolverASeleccion} className="text-xs text-gray-400 hover:text-gray-600 transition">← Cambiar de ejercicio</button>
          <button onClick={onSalir} className="text-xs text-gray-400 hover:text-gray-600 transition">✓ Ya terminé</button>
        </div>
      </div>
    </div>
  );
};

const PantallaDespedida = ({ codigo, onVolver }: any) => {
  const [feedback, setFeedback] = useState<string | null>(null);

  return (
    <div className="min-h-screen flex flex-col">
      <Header codigo={codigo} showExit={false} />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full text-center fade-in">
          <div className="flex justify-center mb-4"><BitRobot size={140} mood="happy" /></div>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">¡Buen trabajo! 🎉</h2>
          <p className="text-gray-600 mb-6">Gracias por hablar conmigo hoy, <span style={{color: '#2E9DF7'}}>{codigo}</span>.</p>
          {feedback === null ? (
            <>
              <p className="text-gray-700 font-semibold mb-4">¿Cómo te sentiste?</p>
              <div className="grid grid-cols-3 gap-2 mb-6">
                <button onClick={() => setFeedback("bien")} className="py-4 bg-green-50 hover:bg-green-100 rounded-xl transition transform hover:scale-105">
                  <div className="text-4xl">😊</div><div className="text-xs mt-1 text-gray-600">¡Genial!</div>
                </button>
                <button onClick={() => setFeedback("regular")} className="py-4 bg-yellow-50 hover:bg-yellow-100 rounded-xl transition transform hover:scale-105">
                  <div className="text-4xl">😐</div><div className="text-xs mt-1 text-gray-600">Más o menos</div>
                </button>
                <button onClick={() => setFeedback("mal")} className="py-4 bg-red-50 hover:bg-red-100 rounded-xl transition transform hover:scale-105">
                  <div className="text-4xl">😞</div><div className="text-xs mt-1 text-gray-600">No mucho</div>
                </button>
              </div>
            </>
          ) : (
            <div className="bg-blue-50 rounded-xl p-4 mb-6 fade-in">
              <p className="text-gray-700">¡Gracias por contarme! Tu profe va a tomar nota. 📝</p>
            </div>
          )}
          <button onClick={onVolver} className="w-full py-3 bg-[#2E9DF7] hover:bg-[#1a8de8] text-white font-bold rounded-xl shadow-md transition">
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  );
};


export default function App() {
  const [pantalla, setPantalla] = useState<"bienvenida" | "asentimiento" | "seleccion" | "chat" | "despedida">("bienvenida");
  const [session, setSession] = useState<SessionData>({ usuario_id: '', codigo_nemonico: '', sesion_id: '', conversacion_id: '' });
  const [ejercicioActual, setEjercicioActual] = useState<any>(null); 
  return (
    <div>
      {pantalla === "bienvenida" && (
        <PantallaBienvenida onEntrar={(codigo: string, userId: string) => { setSession({ ...session, codigo_nemonico: codigo, usuario_id: userId }); setPantalla("asentimiento"); }} />
      )}
      {pantalla === "asentimiento" && (
        <PantallaAsentimiento session={session} 
          onAceptar={(sesionId: string) => { setSession({ ...session, sesion_id: sesionId }); setPantalla("seleccion"); }} 
          onRechazar={() => { setSession({ usuario_id: '', codigo_nemonico: '', sesion_id: '', conversacion_id: '' }); setPantalla("bienvenida"); }} />
      )}
      {pantalla === "seleccion" && (
        <PantallaSeleccion session={session} 
          onSeleccionar={(ej: any, convId: string) => { 
            setSession({ ...session, conversacion_id: convId }); 
            setEjercicioActual(ej); 
            setPantalla("chat"); 
          }} 
          onSalir={() => setPantalla("despedida")} />
      )}
      {pantalla === "chat" && (
        <PantallaChat session={session} ejercicio={ejercicioActual} 
          onVolverASeleccion={() => setPantalla("seleccion")} 
          onSalir={() => setPantalla("despedida")} />
      )}
      {pantalla === "despedida" && (
        <PantallaDespedida codigo={session.codigo_nemonico}
          onVolver={() => { setSession({ usuario_id: '', codigo_nemonico: '', sesion_id: '', conversacion_id: '' }); setEjercicioActual(null); setPantalla("bienvenida"); }} />
      )}
    </div>
  );
}