# SPEC — Motor de clasificación de leads (Liftiva)

Implementa un módulo Python (solo librería estándar, Python 3.11) llamado `classifier.py`
que exponga una función:

```python
def classify(lead: dict) -> dict
```

## Entrada

`lead` es un diccionario con:

| Campo     | Tipo | Descripción |
|-----------|------|-------------|
| `nombre`  | str  | Nombre del prospecto. Puede ser cadena vacía. |
| `mensaje` | str  | Texto libre en español (WhatsApp, formulario o correo). Puede traer errores de ortografía, mayúsculas, sin acentos, modismos mexicanos. |
| `canal`   | str  | `"whatsapp"`, `"formulario"` o `"email"`. |

## Salida

Diccionario con exactamente estas llaves:

```python
{"intencion": str, "urgencia": str, "puntaje": int, "respuesta": str}
```

---

## 1. `intencion`

Una de: `"diagnostico"`, `"proyecto"`, `"implementacion"`, `"soporte"`, `"otro"`.

Catálogo de servicios de Liftiva (para referencia): presencia digital (landing pages /
página web / sitio), canales de atención (WhatsApp, formularios), visibilidad local
(Google Business, Maps, reseñas), redes sociales, mensajes comerciales (copywriting),
automatización (captura de leads, respuestas automáticas, recordatorios de citas, bots),
CRM, y medición (dashboards, métricas, reportes), anuncios/publicidad.

Definiciones:

- **`otro`** — El mensaje NO es de un prospecto: spam, proveedores que ofrecen
  productos/servicios a Liftiva, solicitudes de empleo o vacantes, o mensajes sin
  ninguna relación con contratar los servicios.
- **`soporte`** — El remitente ya es cliente de Liftiva (o refiere a un trabajo que
  Liftiva ya le entregó/que ya contrató) y reporta un **problema o duda sobre lo ya
  entregado**. Importante: si un cliente existente pide **trabajo nuevo**, NO es
  soporte; se clasifica según lo que solicita.
- **`implementacion`** — Pide un ecosistema/solución completa o integral ("todo",
  "paquete completo", "solución integral", "ecosistema", "digitalizar todo el
  negocio"), o solicita **3 o más** servicios distintos del catálogo en el mismo
  mensaje, o pide CRM completo / infraestructura amplia con intención de contratar.
- **`proyecto`** — Pide (o pregunta precio/cotización de) **1 o 2** entregables
  específicos del catálogo (p. ej. una landing page, automatizar WhatsApp, aparecer en
  Google, un dashboard, recordatorios de citas).
- **`diagnostico`** — Interés general: pide información, pregunta cómo trabajan,
  precios en general, pide el diagnóstico inicial gratuito, o el mensaje no permite
  identificar un entregable específico. **Es la categoría por defecto.**

**Precedencia** cuando hay señales de varias categorías:
`otro` > `soporte` > `implementacion` > `proyecto` > `diagnostico`.

## 2. `urgencia`

Una de: `"alta"`, `"media"`, `"baja"`. Se evalúa sobre el texto del mensaje sin importar
la intención.

- **`alta`** — Plazo inmediato o presión explícita: "urgente", "urge", "hoy",
  "lo antes posible", "cuanto antes", "esta semana", "para ya", "lo necesito ya",
  y expresiones equivalentes; o el mensaje describe una **pérdida activa** de
  clientes/ventas/citas/mensajes ("estoy perdiendo clientes", "se pierden los
  mensajes").
- **`media`** — Plazo definido pero no inmediato: "este mes", "el próximo mes",
  "la otra semana", "en las próximas semanas", "pronto", y equivalentes.
- **`baja`** — Sin plazo ni presión (por defecto).

Precedencia: `alta` > `media` > `baja`. Referencias al pasado ("el mes pasado",
"hace un año") NO son señales de plazo.

## 3. `puntaje`

Entero de 0 a 100, calculado de forma **determinista**:

```
puntaje = base(intencion) + bono(urgencia) + bono(presupuesto) + bono(canal)
```

| Componente | Valores |
|---|---|
| base(intencion) | implementacion=40, proyecto=30, soporte=25, diagnostico=20, otro=0 |
| bono(urgencia)  | alta=+30, media=+15, baja=+0 |
| bono(presupuesto) | monto ≥ 35,000 → +20; monto ≥ 8,000 → +10; menor o sin monto → +0 |
| bono(canal)     | whatsapp=+10, formulario=+5, email=+0 |

- Si `intencion == "otro"`, el puntaje es **0** (se ignoran los bonos).
- Tope en 100.

### Detección de presupuesto (montos en MXN)

Un número dentro del mensaje cuenta como monto **solo si** cumple al menos una:
va precedido de `$`; va seguido de `pesos`, `mxn`, `mil` o `k` (donde `mil` y `k`
multiplican por 1,000); o aparece en la misma oración que la palabra "presupuesto".

- Formatos a soportar: `$12,000`, `35,000`, `80 mil pesos`, `100 mil`, `8k`, `5000`.
  Las comas (y puntos seguidos de exactamente 3 dígitos) son separadores de miles.
- Si hay varios montos válidos (p. ej. "entre 20 y 40 mil pesos"), se usa el **mayor**.
- Números que no cumplen las condiciones (teléfonos, cantidades sueltas, años) se
  ignoran.

## 4. `respuesta`

Borrador de primera respuesta en español, tono profesional y cálido, listo para enviar
por el mismo canal. Requisitos verificables:

- Si `intencion == "otro"` → cadena vacía `""`.
- En cualquier otro caso:
  - Si `nombre` no está vacío, la respuesta debe **incluir el nombre** del lead.
  - Debe incluir la palabra clave del siguiente paso según la intención:
    - `diagnostico` → la palabra **"diagnóstico"** (ofrecer el diagnóstico inicial gratuito)
    - `proyecto` → la palabra **"propuesta"** (ofrecer preparar una propuesta con alcance y precio)
    - `implementacion` → la palabra **"llamada"** (invitar a agendar una llamada)
    - `soporte` → la palabra **"revisar"** (comprometerse a revisar el problema)

## Restricciones

- Un solo archivo `classifier.py`, solo librería estándar de Python.
- Sin llamadas a red ni a modelos de lenguaje: la clasificación es por reglas/heurísticas.
- El código debe ser robusto a mayúsculas, falta de acentos y signos de puntuación.
