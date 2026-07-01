"""Motor de clasificación de leads para Liftiva.

Implementación de referencia (Fable 5) de SPEC.md: clasifica intención y
urgencia de un mensaje entrante, calcula un puntaje determinista y genera
un borrador de primera respuesta.
"""

import re
import unicodedata


def _norm(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar de forma robusta."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _tiene(texto: str, frases) -> bool:
    return any(f in texto for f in frases)


def _tiene_palabra(texto: str, palabras) -> bool:
    return any(re.search(r"\b" + re.escape(p) + r"\b", texto) for p in palabras)


# --- Intención -------------------------------------------------------------

_OTRO = [
    "vendo", "vendemos", "le ofrecemos", "les ofrecemos", "promocion valida",
    "vacante", "busco empleo", "busco trabajo", "solicito empleo",
    "soy proveedor", "somos proveedores", "seguidores para",
]

_CLIENTE = [
    "ya soy cliente", "soy cliente", "soy su cliente",
    "me hicieron", "hicieron ustedes", "ustedes hicieron",
    "ustedes armaron", "que me armaron", "me entregaron",
    "contrate", "con ustedes",
]

_PROBLEMA = [
    "no funciona", "no me funciona", "no carga", "no esta cargando",
    "no sirve", "dejo de funcionar", "se cayo", "problema", "error",
    "falla", "duda", "se pierden", "se me pierden", "no llegan",
]

_INTEGRAL = [
    "integral", "paquete completo", "ecosistema", "todo mi", "toda mi",
    "todo el negocio", "toda la presencia", "de todo", "todo pues",
    "crm completo", "infraestructura",
]

# Grupos de servicios del catálogo; cada grupo cuenta una sola vez.
_SERVICIOS = {
    "web": ["landing", "pagina", "sitio", "web"],
    "whatsapp": ["whatsapp", "whats"],
    "google": ["google", "maps", "resenas", "resena", "google business"],
    "redes": ["redes sociales", "instagram", "facebook"],
    "crm": ["crm"],
    "medicion": ["dashboard", "metricas", "medicion", "reportes"],
    "automatizacion": ["automatiz", "recordatorio", "respuestas automaticas",
                       "bot", "automatico", "automatica"],
    "anuncios": ["anuncios", "publicidad", "ads", "campanas"],
    "copy": ["copywriting", "propuesta de valor"],
}


def _grupos_servicio(texto: str) -> int:
    return sum(1 for claves in _SERVICIOS.values() if _tiene(texto, claves))


def _intencion(texto: str) -> str:
    if _tiene(texto, _OTRO):
        return "otro"
    if _tiene(texto, _CLIENTE) and _tiene(texto, _PROBLEMA):
        return "soporte"
    if _tiene(texto, _INTEGRAL) or _grupos_servicio(texto) >= 3:
        return "implementacion"
    if _grupos_servicio(texto) >= 1:
        return "proyecto"
    return "diagnostico"


# --- Urgencia ---------------------------------------------------------------

_ALTA_FRASES = [
    "urgent", "lo antes posible", "cuanto antes", "esta semana",
    "para ya", "lo necesito ya", "de inmediato", "ahorita mismo",
    "estoy perdiendo", "estamos perdiendo", "se pierden", "se me pierden",
    "pierdo clientes", "pierdo ventas", "perdiendo",
]
_ALTA_PALABRAS = ["urge", "hoy", "urgentisimo"]

_MEDIA_FRASES = [
    "este mes", "proximo mes", "el mes que entra", "proximas semanas",
    "la otra semana", "la proxima semana", "la semana que entra",
    "en unas semanas", "pronto",
]


def _urgencia(texto: str) -> str:
    if _tiene(texto, _ALTA_FRASES) or _tiene_palabra(texto, _ALTA_PALABRAS):
        return "alta"
    if _tiene(texto, _MEDIA_FRASES):
        return "media"
    return "baja"


# --- Presupuesto ------------------------------------------------------------

_NUM = re.compile(
    r"(\$\s*)?(\d{1,3}(?:,\d{3})+|\d{1,3}(?:\.\d{3})+|\d+)\s*(mil|k|pesos|mxn)?\b",
    re.IGNORECASE,
)


def _monto_maximo(texto: str) -> int:
    """Mayor monto en MXN detectado en el mensaje, o 0 si no hay."""
    mayor = 0
    for oracion in re.split(r"[.!?\n]+", texto):
        con_presupuesto = "presupuesto" in oracion
        for signo, numero, sufijo in _NUM.findall(oracion):
            sufijo = sufijo.lower()
            valido = bool(signo) or sufijo in ("mil", "k", "pesos", "mxn") or con_presupuesto
            if not valido:
                continue
            valor = float(numero.replace(",", "").replace(".", ""))
            if sufijo in ("mil", "k"):
                valor *= 1000
            mayor = max(mayor, int(valor))
    return mayor


def _bono_presupuesto(monto: int) -> int:
    if monto >= 35000:
        return 20
    if monto >= 8000:
        return 10
    return 0


# --- Puntaje ----------------------------------------------------------------

_BASE = {"implementacion": 40, "proyecto": 30, "soporte": 25,
         "diagnostico": 20, "otro": 0}
_BONO_URGENCIA = {"alta": 30, "media": 15, "baja": 0}
_BONO_CANAL = {"whatsapp": 10, "formulario": 5, "email": 0}


def _puntaje(intencion: str, urgencia: str, monto: int, canal: str) -> int:
    if intencion == "otro":
        return 0
    total = (_BASE[intencion] + _BONO_URGENCIA[urgencia]
             + _bono_presupuesto(monto) + _BONO_CANAL.get(canal, 0))
    return min(total, 100)


# --- Respuesta --------------------------------------------------------------

_PASOS = {
    "diagnostico": (
        "gracias por escribirnos a Liftiva. Con gusto te compartimos toda la "
        "información; el primer paso es un diagnóstico inicial sin costo para "
        "identificar qué es lo que más le conviene a tu negocio. ¿Te parece si "
        "lo agendamos?"
    ),
    "proyecto": (
        "gracias por contactar a Liftiva. Claro que podemos ayudarte: con unos "
        "cuantos datos de tu negocio te preparamos una propuesta con alcance, "
        "tiempos y precio. ¿Me cuentas un poco más de lo que necesitas?"
    ),
    "implementacion": (
        "gracias por escribir a Liftiva. Lo que buscas es justo lo que armamos: "
        "un sistema completo para tu negocio. Lo mejor es agendar una llamada "
        "breve para entender tu operación y proponerte el plan adecuado. "
        "¿Qué día te acomoda?"
    ),
    "soporte": (
        "una disculpa por el inconveniente. Ya lo estamos atendiendo: vamos a "
        "revisar tu caso de inmediato y te confirmamos por este medio en cuanto "
        "quede resuelto."
    ),
}


def _respuesta(intencion: str, nombre: str) -> str:
    if intencion == "otro":
        return ""
    saludo = f"Hola {nombre.strip()}, " if nombre.strip() else "Hola, "
    return saludo + _PASOS[intencion]


# --- API pública ------------------------------------------------------------

def classify(lead: dict) -> dict:
    nombre = lead.get("nombre", "") or ""
    canal = (lead.get("canal", "") or "").strip().lower()
    texto = _norm(lead.get("mensaje", "") or "")

    intencion = _intencion(texto)
    urgencia = _urgencia(texto)
    monto = _monto_maximo(texto)

    return {
        "intencion": intencion,
        "urgencia": urgencia,
        "puntaje": _puntaje(intencion, urgencia, monto, canal),
        "respuesta": _respuesta(intencion, nombre),
    }
