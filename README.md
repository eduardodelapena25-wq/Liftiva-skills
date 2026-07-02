# Liftiva — Motor de clasificación de leads + benchmark Fable 5 vs Opus

> **Otros apartados de este repositorio**
>
> - [`control-remoto-pc/`](control-remoto-pc/README.md) — guía y scripts para
>   controlar la PC de escritorio (2 monitores) desde la laptop con
>   Sunshine + Moonlight. En Claude Code escribe `/control-remoto-pc` para que
>   Claude te guíe paso a paso.

Ejemplo práctico construido a partir del análisis de [liftivamx.com](https://liftivamx.com),
diseñado además como banco de pruebas para comparar modelos (Fable 5 vs Opus) en una
tarea real del negocio. Ver `BENCHMARK.md` para el protocolo de comparación.

## Análisis de liftivamx.com (resumen)

Liftiva (Monterrey, N.L.) vende **infraestructura digital para negocios locales** que ya
venden pero operan desorganizados. Lo más sólido de la página:

- **Posicionamiento honesto**: "construimos infraestructura, no resultados garantizados".
  Poco común en el sector y genera confianza.
- **6 servicios claros**: presencia digital, canales de atención, visibilidad local,
  mensajes comerciales, **automatización (captura, clasificación y seguimiento de
  leads)** y medición.
- **Prueba social con métricas**: Despacho Garza (+38% consultas en 30 días), Clínica
  Dental Sáenz (0 citas perdidas, +52% tasa de respuesta).
- **Precios transparentes**: diagnóstico gratis, proyectos $8,000–$35,000 MXN,
  implementación completa $35,000–$120,000+ MXN.
- **Compromiso operativo**: respuesta en menos de 2 horas en horario hábil.

## El ejemplo práctico

De los 6 servicios, elegí construir el que Liftiva vende pero (según la página) opera
sobre WhatsApp/formulario/correo fragmentados: un **motor de clasificación de leads**.
Es exactamente el producto del pilar de "Automatización", aplicado a Liftiva misma —
sirve de demo para clientes y de herramienta interna.

Dado un mensaje entrante, el motor devuelve:

- **`intencion`** — qué quiere: `diagnostico` (gratis), `proyecto` ($8–35k),
  `implementacion` ($35k+), `soporte` (cliente existente) u `otro` (spam/vacantes).
  Las tres primeras se alinean con los tiers de precios de la página.
- **`urgencia`** — `alta` / `media` / `baja` según plazos y señales de pérdida activa.
- **`puntaje`** — 0–100 determinista (valor del tier + urgencia + presupuesto detectado
  en el texto + canal), para ordenar a quién responder primero.
- **`respuesta`** — borrador de primera respuesta listo para enviar, que ayuda a cumplir
  el compromiso de "menos de 2 horas".

### Probarlo

```bash
python3 demo.py                      # clasifica 3 leads de ejemplo
python3 run_eval.py                  # califica todas las implementaciones (36 casos)
python3 run_eval.py -v fable5        # detalle de fallas de una implementación
```

Resultado de la comparación (56 casos, dos exámenes cruzados — ver `INFORME.md`):
**Fable 5 = 92.9/100 · Opus = 84.6/100**.

## Estructura

```
SPEC.md                              # especificación (lo único que ve cada modelo)
implementations/fable5/classifier.py # implementación de Fable 5
implementations/opus/                # aquí va la de Opus (ver BENCHMARK.md)
eval/leads_eval.json                 # 36 leads etiquetados (fácil/medio/difícil)
run_eval.py                          # evaluador automático
demo.py                              # demostración rápida
BENCHMARK.md                         # protocolo de comparación y métricas
```

## Cómo medir contra Opus

En corto (detalle en `BENCHMARK.md`):

1. Pégale a Opus el prompt de `BENCHMARK.md` + `SPEC.md` en una sesión nueva.
2. Guarda su código en `implementations/opus/classifier.py` sin corregirle nada.
3. `python3 run_eval.py` — la tabla comparativa sale sola.
4. Para que sea justo de verdad, agrega leads reales de tu WhatsApp al eval como
   casos ciegos: ningún modelo los vio y son los que más importan.
