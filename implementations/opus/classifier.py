import re
import unicodedata

INTENCIONES = ("diagnostico", "proyecto", "implementacion", "soporte", "otro")


def _strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalize(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    text = text.lower()
    text = _strip_accents(text)
    text = text.replace(" ", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Servicios del catalogo -> conjuntos de palabras clave (ya normalizadas)
# ---------------------------------------------------------------------------
SERVICIOS = {
    "presencia_digital": [
        "landing", "landing page", "pagina web", "paginas web", "sitio web",
        "sitio", "pagina", "website", "web site", "portal",
    ],
    "canales_atencion": [
        "whatsapp", "whats app", "wa", "formulario", "formularios",
        "canal de atencion", "canales de atencion", "chat",
    ],
    "visibilidad_local": [
        "google business", "google my business", "google maps", "maps",
        "resenas", "resena", "reviews", "ficha de google", "aparecer en google",
        "visibilidad local", "google",
    ],
    "redes_sociales": [
        "redes sociales", "redes", "instagram", "facebook", "tiktok",
        "social media", "fanpage", "fan page",
    ],
    "mensajes_comerciales": [
        "copywriting", "copy", "mensajes comerciales", "textos", "redaccion",
        "redactar",
    ],
    "automatizacion": [
        "automatizacion", "automatizar", "automatico", "automaticos",
        "automatica", "automaticas", "respuestas automaticas", "bot", "bots",
        "chatbot", "recordatorio", "recordatorios", "recordatorio de cita",
        "recordatorios de citas", "captura de leads", "captura de prospectos",
    ],
    "crm": ["crm"],
    "medicion": [
        "dashboard", "dashboards", "metrica", "metricas", "reporte",
        "reportes", "medicion", "medir", "kpi", "kpis", "analitica",
        "estadisticas", "tablero",
    ],
    "anuncios": [
        "anuncio", "anuncios", "publicidad", "ads", "google ads",
        "facebook ads", "campana", "campanas", "pauta",
    ],
}


def _detect_services(text: str) -> set:
    """Devuelve el conjunto de categorias de servicio mencionadas."""
    found = set()
    for categoria, palabras in SERVICIOS.items():
        for palabra in palabras:
            # frontera de palabra basica para evitar coincidencias parciales
            if re.search(r"\b" + re.escape(palabra) + r"\b", text):
                found.add(categoria)
                break
    return found


# ---------------------------------------------------------------------------
# Deteccion de "otro" (no es prospecto)
# ---------------------------------------------------------------------------
OTRO_PATRONES = [
    r"\boferta laboral\b",
    r"\bofrezco mis servicios\b",
    r"\bles ofrezco\b",
    r"\ble ofrezco\b",
    r"\bofrecemos\b",
    r"\bofrecer\b",
    r"\bsomos (?:una |un )?(?:empresa|proveedor|distribuidor|agencia|fabrica)\b",
    r"\bproveedor\b",
    r"\bdistribuidor\b",
    r"\bmayoreo\b",
    r"\bcotizacion (?:de|para) (?:material|productos)\b",
    r"\bbusco (?:empleo|trabajo|vacante|chamba)\b",
    r"\bsolicito (?:empleo|trabajo)\b",
    r"\bvacante\b",
    r"\bvacantes\b",
    r"\bcurriculum\b",
    r"\bcv\b",
    r"\bmi cv\b",
    r"\bhoja de vida\b",
    r"\bpostular\b",
    r"\bpostularme\b",
    r"\baplicar (?:a|al|para) (?:el |la )?(?:puesto|vacante|empleo)\b",
    r"\bpuesto de trabajo\b",
    r"\bestoy interesado en trabajar (?:con|en|para)\b",
    r"\bme gustaria trabajar (?:con|en|para) ustedes\b",
    r"\bpremio\b",
    r"\bhas ganado\b",
    r"\bganaste\b",
    r"\bhaz ganado\b",
    r"\bclick aqui\b",
    r"\bhaz clic\b",
    r"\bcriptomoneda\b",
    r"\bbitcoin\b",
    r"\bprestamo\b",
    r"\bprestamos\b",
    r"\bviagra\b",
    r"\bcasino\b",
    r"\bloteria\b",
    r"\bherencia\b",
]

# Frases que indican que quien escribe ofrece algo A Liftiva (spam de proveedor).
OTRO_OFRECE_A_LIFTIVA = [
    r"\bofrecerle(?:s)?\b",
    r"\bofrecerte\b",
    r"\bvendemos\b",
    r"\bvendo\b",
    r"\ble vendo\b",
    r"\bles vendo\b",
]


def _es_otro(text: str) -> bool:
    for pat in OTRO_PATRONES:
        if re.search(pat, text):
            return True
    for pat in OTRO_OFRECE_A_LIFTIVA:
        if re.search(pat, text):
            return True
    return False


# ---------------------------------------------------------------------------
# Deteccion de "soporte" (ya es cliente y reporta problema/duda de lo entregado)
# ---------------------------------------------------------------------------
SOPORTE_CLIENTE = [
    r"\bya soy cliente\b",
    r"\bsoy cliente\b",
    r"\bsoy su cliente\b",
    r"\bsoy cliente de ustedes\b",
    r"\bya trabajamos (?:juntos|con ustedes)\b",
    r"\bya trabaje con ustedes\b",
    r"\bme (?:hicieron|entregaron|instalaron|desarrollaron|crearon|montaron)\b",
    r"\bustedes me (?:hicieron|entregaron|instalaron|desarrollaron|crearon|montaron)\b",
    r"\bla (?:pagina|landing|web|automatizacion) que me (?:hicieron|entregaron|crearon)\b",
    r"\bel (?:sitio|bot|dashboard|crm) que me (?:hicieron|entregaron|crearon|montaron)\b",
    r"\bque me (?:hicieron|entregaron|instalaron|desarrollaron|crearon|montaron)\b",
    r"\bque me entregaron\b",
    r"\bque contrate con ustedes\b",
    r"\bque ya (?:contrate|pague)\b",
    r"\bmi (?:pagina|landing|sitio|bot|dashboard|crm|automatizacion) (?:con ustedes|de liftiva)\b",
    r"\bel proyecto que me (?:entregaron|hicieron)\b",
]

SOPORTE_PROBLEMA = [
    r"\bno funciona\b",
    r"\bno sirve\b",
    r"\bno jala\b",
    r"\bdejo de funcionar\b",
    r"\bdejaron de funcionar\b",
    r"\bno me llega\b",
    r"\bno llegan\b",
    r"\bno estan llegando\b",
    r"\bno carga\b",
    r"\bno abre\b",
    r"\bno responde\b",
    r"\btiene un (?:error|problema|bug|fallo|falla)\b",
    r"\bhay un (?:error|problema|bug|fallo|falla)\b",
    r"\bda error\b",
    r"\bmarca error\b",
    r"\bse cayo\b",
    r"\besta caido\b",
    r"\bse (?:trabo|traba|congelo)\b",
    r"\bproblema con\b",
    r"\bfalla\b",
    r"\bfallando\b",
    r"\bbug\b",
    r"\bdejo de (?:enviar|mandar|funcionar|servir)\b",
    r"\bya no (?:funciona|sirve|manda|envia|llega|carga|responde|jala)\b",
    r"\bnecesito ayuda con\b",
    r"\bayuda con (?:mi|el|la)\b",
    r"\bduda (?:sobre|con|de) (?:mi|el|la)\b",
    r"\btengo una duda (?:sobre|con|de)\b",
    r"\bno se como usar\b",
    r"\bcomo (?:uso|edito|cambio|actualizo)\b",
]

# Peticion de trabajo NUEVO (anula soporte)
TRABAJO_NUEVO = [
    r"\bahora quiero\b",
    r"\bahora necesito\b",
    r"\btambien quiero\b",
    r"\btambien necesito\b",
    r"\bademas quiero\b",
    r"\bademas necesito\b",
    r"\bquiero (?:otra|otro|una nueva|un nuevo|agregar|sumar)\b",
    r"\bnecesito (?:otra|otro|una nueva|un nuevo|agregar|sumar)\b",
    r"\bquiero contratar (?:otro|otra|mas|ademas|tambien)\b",
    r"\bnuevo proyecto\b",
    r"\botro proyecto\b",
]


def _es_soporte(text: str) -> bool:
    es_cliente = any(re.search(p, text) for p in SOPORTE_CLIENTE)
    if not es_cliente:
        return False
    pide_nuevo = any(re.search(p, text) for p in TRABAJO_NUEVO)
    if pide_nuevo:
        return False
    reporta_problema = any(re.search(p, text) for p in SOPORTE_PROBLEMA)
    return reporta_problema


# ---------------------------------------------------------------------------
# Deteccion de "implementacion" (solucion integral / 3+ servicios / CRM completo)
# ---------------------------------------------------------------------------
IMPLEMENTACION_FRASES = [
    r"\btodo el (?:paquete|ecosistema|proyecto)\b",
    r"\bpaquete completo\b",
    r"\bsolucion integral\b",
    r"\bsolucion completa\b",
    r"\becosistema\b",
    r"\bdigitalizar (?:todo )?(?:mi|el) negocio\b",
    r"\bdigitalizar todo\b",
    r"\btodo mi negocio\b",
    r"\btodo el negocio\b",
    r"\bde todo un poco\b",
    r"\bquiero todo\b",
    r"\bnecesito todo\b",
    r"\btodo lo que (?:ofrecen|manejan|hacen)\b",
    r"\bde principio a fin\b",
    r"\bllave en mano\b",
    r"\binfraestructura (?:digital|completa)\b",
    r"\bcrm completo\b",
    r"\btransformacion digital\b",
]


def _es_implementacion(text: str, servicios: set) -> bool:
    if any(re.search(p, text) for p in IMPLEMENTACION_FRASES):
        return True
    if len(servicios) >= 3:
        return True
    return False


# ---------------------------------------------------------------------------
# Deteccion de "proyecto"
# ---------------------------------------------------------------------------
PROYECTO_VERBOS = [
    r"\bquiero\b", r"\bnecesito\b", r"\brequiero\b", r"\bme interesa\b",
    r"\bbusco\b", r"\bocupo\b", r"\bpuedo contratar\b", r"\bcontratar\b",
    r"\bcotiza(?:r|cion)?\b", r"\bpresupuesto\b", r"\bcuanto (?:cuesta|cobran|vale|es|sale)\b",
    r"\bprecio\b", r"\bme (?:hacen|pueden hacer|arman|desarrollan)\b",
    r"\bme gustaria\b", r"\bhacer\b", r"\bcrear\b", r"\bdisenar\b",
    r"\bimplementar\b", r"\bponer\b", r"\bmontar\b", r"\barmar\b",
    r"\baparecer en\b", r"\bautomatizar\b",
]


def _es_proyecto(text: str, servicios: set) -> bool:
    if not servicios:
        return False
    # 1 o 2 servicios + alguna senal de peticion/precio
    if any(re.search(p, text) for p in PROYECTO_VERBOS):
        return True
    return False


# ---------------------------------------------------------------------------
# Clasificacion de intencion (con precedencia)
# ---------------------------------------------------------------------------
def _clasificar_intencion(text: str) -> str:
    if _es_otro(text):
        return "otro"
    if _es_soporte(text):
        return "soporte"
    servicios = _detect_services(text)
    if _es_implementacion(text, servicios):
        return "implementacion"
    if _es_proyecto(text, servicios):
        return "proyecto"
    return "diagnostico"


# ---------------------------------------------------------------------------
# Urgencia
# ---------------------------------------------------------------------------
URGENCIA_ALTA = [
    r"\burgente\b", r"\burge\b", r"\burgen\b", r"\burgemos\b",
    r"\bhoy\b", r"\bhoy mismo\b", r"\bya\b(?! (?:soy|contrate|pague|tengo))",
    r"\blo antes posible\b", r"\blo mas pronto posible\b", r"\bcuanto antes\b",
    r"\bde inmediato\b", r"\binmediato\b", r"\binmediatamente\b",
    r"\besta semana\b", r"\bpara ya\b", r"\blo necesito ya\b",
    r"\bpara hoy\b", r"\bpara ayer\b", r"\bemergencia\b",
    r"\bno puede esperar\b", r"\bcorriendo\b", r"\bapremio\b",
    r"\bmanana(?: mismo)?\b",
]

# Perdida activa de clientes/ventas/citas/mensajes
URGENCIA_PERDIDA = [
    r"\bestoy perdiendo\b",
    r"\bperdiendo (?:clientes|ventas|citas|mensajes|dinero|prospectos)\b",
    r"\bse (?:me )?(?:pierden|estan perdiendo|escapan|van) (?:los |las )?(?:mensajes|clientes|ventas|citas|prospectos)\b",
    r"\bse pierden (?:los )?mensajes\b",
    r"\bpierdo (?:clientes|ventas|citas|mensajes|prospectos|dinero)\b",
    r"\bno (?:alcanzo|doy abasto) a (?:contestar|responder)\b",
    r"\bse me (?:escapan|van) (?:los )?clientes\b",
    r"\bestoy dejando de (?:vender|atender)\b",
]

URGENCIA_MEDIA = [
    r"\beste mes\b",
    r"\bel proximo mes\b",
    r"\bproximo mes\b",
    r"\bel mes que (?:viene|entra)\b",
    r"\bmes que (?:viene|entra)\b",
    r"\bla (?:otra|proxima) semana\b",
    r"\bproxima semana\b",
    r"\ben (?:las )?proximas semanas\b",
    r"\bproximas semanas\b",
    r"\bpronto\b",
    r"\ben unos dias\b",
    r"\ben los proximos dias\b",
    r"\ben un par de semanas\b",
    r"\ben este trimestre\b",
    r"\bantes de fin de mes\b",
]


def _clasificar_urgencia(text: str) -> str:
    for pat in URGENCIA_ALTA:
        if re.search(pat, text):
            return "alta"
    for pat in URGENCIA_PERDIDA:
        if re.search(pat, text):
            return "alta"
    for pat in URGENCIA_MEDIA:
        if re.search(pat, text):
            return "media"
    return "baja"


# ---------------------------------------------------------------------------
# Deteccion de presupuesto (montos MXN)
# ---------------------------------------------------------------------------
def _split_oraciones(text: str) -> list:
    partes = re.split(r"[.!?;\n]+", text)
    return [p.strip() for p in partes if p.strip()]


def _parse_number(raw: str) -> float | None:
    """Convierte '12,000' / '35.000' / '5000' / '80' a numero, tratando comas y
    puntos seguidos de exactamente 3 digitos como separadores de miles."""
    s = raw.strip()
    if not re.fullmatch(r"[0-9][0-9.,]*", s):
        return None
    # Separadores de miles: coma o punto seguido de exactamente 3 digitos.
    # Eliminamos las comas siempre (separador de miles).
    s = s.replace(",", "")
    # Puntos seguidos de exactamente 3 digitos (y al final o antes de otro grupo) -> miles
    # Estrategia: si el punto va seguido de exactamente 3 digitos, es separador de miles.
    def _repl(m):
        return m.group(1)
    # Quitar puntos separadores de miles (punto + 3 digitos que no formen decimal real)
    while re.search(r"\.\d{3}(?!\d)", s):
        s = re.sub(r"\.(\d{3})(?!\d)", r"\1", s, count=1)
    if not re.fullmatch(r"\d+(?:\.\d+)?", s):
        # residuo raro
        s = re.sub(r"[^\d]", "", s)
        if not s:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def _detectar_presupuesto(text: str) -> int:
    """Devuelve el mayor monto valido (MXN) detectado, o 0 si no hay."""
    montos = []
    oraciones = _split_oraciones(text)

    num_token = r"\d[\d.,]*"

    for oracion in oraciones:
        tiene_presupuesto = bool(re.search(r"\bpresupuesto\b", oracion))

        # 1) Numero precedido de $  (opcional con mil/k despues)
        for m in re.finditer(
            r"\$\s*(" + num_token + r")\s*(mil|k)?\b", oracion
        ):
            val = _parse_number(m.group(1))
            if val is None:
                continue
            mult = 1000 if m.group(2) in ("mil", "k") else 1
            montos.append(val * mult)

        # 2) Numero seguido de pesos/mxn/mil/k
        for m in re.finditer(
            r"(" + num_token + r")\s*(mil|k|pesos|mxn|varos|lucas)\b", oracion
        ):
            val = _parse_number(m.group(1))
            if val is None:
                continue
            unidad = m.group(2)
            mult = 1000 if unidad in ("mil", "k", "lucas") else 1
            montos.append(val * mult)

        # 3) Numeros en la misma oracion que "presupuesto"
        if tiene_presupuesto:
            # Buscar numeros que puedan ir con mil/k tambien
            for m in re.finditer(
                r"(?<![\w$])(" + num_token + r")\s*(mil|k|pesos|mxn)?\b", oracion
            ):
                val = _parse_number(m.group(1))
                if val is None:
                    continue
                mult = 1000 if m.group(2) in ("mil", "k") else 1
                montos.append(val * mult)

    if not montos:
        return 0
    return int(max(montos))


def _bono_presupuesto(monto: int) -> int:
    if monto >= 35000:
        return 20
    if monto >= 8000:
        return 10
    return 0


# ---------------------------------------------------------------------------
# Puntaje
# ---------------------------------------------------------------------------
BASE_INTENCION = {
    "implementacion": 40,
    "proyecto": 30,
    "soporte": 25,
    "diagnostico": 20,
    "otro": 0,
}
BONO_URGENCIA = {"alta": 30, "media": 15, "baja": 0}
BONO_CANAL = {"whatsapp": 10, "formulario": 5, "email": 0}


def _calcular_puntaje(intencion: str, urgencia: str, monto: int, canal: str) -> int:
    if intencion == "otro":
        return 0
    puntaje = BASE_INTENCION.get(intencion, 20)
    puntaje += BONO_URGENCIA.get(urgencia, 0)
    puntaje += _bono_presupuesto(monto)
    puntaje += BONO_CANAL.get(_normalize(canal), 0)
    return min(puntaje, 100)


# ---------------------------------------------------------------------------
# Respuesta
# ---------------------------------------------------------------------------
def _primer_nombre(nombre: str) -> str:
    if not nombre:
        return ""
    partes = nombre.strip().split()
    return partes[0] if partes else ""


def _generar_respuesta(intencion: str, nombre: str, urgencia: str) -> str:
    if intencion == "otro":
        return ""

    saludo_nombre = ""
    nombre_limpio = nombre.strip() if isinstance(nombre, str) else ""
    if nombre_limpio:
        saludo_nombre = f" {_primer_nombre(nombre_limpio)}"

    saludo = f"Hola{saludo_nombre}, gracias por contactar a Liftiva."

    cierre_urgencia = ""
    if urgencia == "alta":
        cierre_urgencia = " Entendemos que es urgente, así que le damos prioridad de inmediato."
    elif urgencia == "media":
        cierre_urgencia = " Con gusto lo atendemos dentro de los tiempos que necesita."

    if intencion == "diagnostico":
        cuerpo = (
            " Con gusto le ayudamos. Para empezar, le ofrecemos sin costo nuestro "
            "diagnóstico inicial gratuito, donde revisamos su negocio y detectamos "
            "las mejores oportunidades para atraer más clientes."
        )
    elif intencion == "proyecto":
        cuerpo = (
            " Perfecto, con gusto preparamos una propuesta con el alcance y el precio "
            "de lo que necesita. Cuéntenos un par de detalles más y se la enviamos."
        )
    elif intencion == "implementacion":
        cuerpo = (
            " Suena a un proyecto integral y nos encantaría ayudarle. Le proponemos "
            "agendar una llamada breve para entender bien su negocio y diseñar la "
            "solución completa a su medida."
        )
    elif intencion == "soporte":
        cuerpo = (
            " Lamentamos el inconveniente. Vamos a revisar de inmediato lo que nos "
            "reporta sobre su servicio y le damos una solución lo antes posible."
        )
    else:
        cuerpo = " Con gusto le ayudamos."

    return (saludo + cuerpo + cierre_urgencia).strip()


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------
def classify(lead: dict) -> dict:
    if not isinstance(lead, dict):
        lead = {}

    nombre_raw = lead.get("nombre", "") or ""
    mensaje_raw = lead.get("mensaje", "") or ""
    canal_raw = lead.get("canal", "") or ""

    if not isinstance(nombre_raw, str):
        nombre_raw = str(nombre_raw)
    if not isinstance(mensaje_raw, str):
        mensaje_raw = str(mensaje_raw)

    texto_norm = _normalize(mensaje_raw)

    intencion = _clasificar_intencion(texto_norm)
    urgencia = _clasificar_urgencia(texto_norm)
    monto = _detectar_presupuesto(texto_norm)
    puntaje = _calcular_puntaje(intencion, urgencia, monto, canal_raw)
    respuesta = _generar_respuesta(intencion, nombre_raw, urgencia)

    return {
        "intencion": intencion,
        "urgencia": urgencia,
        "puntaje": puntaje,
        "respuesta": respuesta,
    }


if __name__ == "__main__":
    ejemplos = [
        {
            "nombre": "Juan Pérez",
            "mensaje": "Hola, quiero una landing page para mi negocio, ¿cuánto cuesta?",
            "canal": "whatsapp",
        },
        {
            "nombre": "",
            "mensaje": "URGENTE se me pierden los mensajes de whatsapp y estoy perdiendo clientes",
            "canal": "whatsapp",
        },
        {
            "nombre": "María",
            "mensaje": "Quiero digitalizar todo mi negocio: pagina web, whatsapp automatico y un dashboard. Presupuesto de 80 mil pesos",
            "canal": "formulario",
        },
        {
            "nombre": "Pedro",
            "mensaje": "La pagina que me hicieron ya no carga, tiene un error",
            "canal": "email",
        },
        {
            "nombre": "Ana",
            "mensaje": "Les ofrezco servicio de limpieza para oficinas, tenemos buen precio",
            "canal": "email",
        },
        {
            "nombre": "Luis",
            "mensaje": "Hola, me gustaría información de cómo trabajan y sus precios en general",
            "canal": "whatsapp",
        },
    ]
    import json
    for e in ejemplos:
        print(json.dumps(classify(e), ensure_ascii=False, indent=2))
