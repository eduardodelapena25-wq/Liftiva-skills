# Informe: Fable 5 vs Opus — Motor de leads Liftiva

**Fecha:** 2026-07-01 · **Tarea:** implementar `SPEC.md` (clasificador de leads) en un
intento, sin ver el examen. **Evaluación cruzada:** cada modelo redactó también un set
de evaluación a partir de la spec; ambas implementaciones se calificaron con los dos
sets (56 casos en total).

## Resultados (puntuación 0–100)

| Set de evaluación | Fable 5 | Opus |
|---|---|---|
| Examen redactado por Fable 5 (36 casos) | **100.0** | 87.8 |
| Examen redactado por Opus (20 casos) | **80.0** | 79.0 |
| **Combinado (56 casos)** | **92.9** | **84.6** |

Pesos por caso: intención 40, urgencia 20, puntaje exacto 25, respuesta 15.

### Análisis de sensibilidad

El 60% de las fallas de Opus viene de una sola decisión: su respuesta saluda solo con
el **primer nombre** ("Hola Rosa" para "Rosa María"), y la spec pide incluir el nombre
del lead (requisito verificable). Relajando ese check para aceptar solo el primer
nombre:

| Set | Fable 5 | Opus |
|---|---|---|
| Examen de Fable 5 | **100.0** | 91.1 |
| Examen de Opus | 80.0 | **88.0** |
| **Combinado** | **92.9** | 90.0 |

Lectura objetiva: **cada modelo gana su propio examen** (la "ventaja de local" existe y
opera en ambas direcciones — por eso se hizo evaluación cruzada). En el combinado,
Fable 5 queda arriba en ambos escenarios: **+8.3 puntos** con el check estricto de la
spec y **+2.9** con el check relajado.

## Hallazgos cualitativos

**Opus — fortalezas:** cobertura léxica muy amplia (594 líneas, vocabulario extenso de
spam, modismos, variantes); 100% en urgencia en ambos sets; en su propio examen con
check relajado superó a Fable 5.

**Opus — debilidades observadas:**
- Truncar el nombre del lead violó un requisito verificable de la spec (costó ~5–9 pts).
- Fronteras de palabra demasiado rígidas: "automatizarlo" no activa `\bautomatizar\b`,
  "no está cargando" no activa "no carga", "contraté" no activa "contratar" → 4 errores
  de intención en el examen de Fable 5.
- Como examinador, calculó mal el puntaje de **2 de sus 20 casos** (se corrigieron con
  la fórmula de la spec antes de calificar; original preservado en
  `eval/leads_eval_opus_original.json`).
- Entregó el código con preámbulo y cercas de markdown pese a la instrucción de
  entregar solo código (se extrajo mecánicamente, sin corregir nada).

**Fable 5 — fortalezas:** 100% en su propio examen; cumplimiento estricto de todos los
requisitos verificables de la respuesta; 100% en urgencia en ambos sets; 3.5× menos
código (209 líneas) con el mismo o mejor desempeño.

**Fable 5 — debilidades observadas (5 fallas, todas en el examen de Opus):** frases de
cliente/problema que no estaban en sus listas ("me instalaron", "no está enviando"),
un proveedor de hosting redactado sin las señales típicas de spam, y contar el sitio
ya entregado como servicio solicitado (clasificó `implementacion` donde era `proyecto`).

## Limitaciones

- Ambos exámenes fueron redactados por los propios contendientes; la evaluación cruzada
  mitiga pero no elimina el sesgo. Los casos que más pesan siguen siendo **leads reales**
  (instrucciones para agregarlos en `BENCHMARK.md`).
- Una sola muestra one-shot por modelo; con retroalimentación iterativa ambos subirían.
- La tarea es de reglas/heurísticas; no mide otras dimensiones (razonamiento largo,
  agentes, etc.).

## Conclusión

En esta tarea real de Liftiva, medida con 56 casos y dos examinadores independientes,
**Fable 5 terminó arriba en el combinado bajo los dos criterios de calificación**
(92.9 vs 84.6 estricto; 92.9 vs 90.0 relajado), con un tercio del código y sin
violaciones de formato ni de spec. Opus mostró mayor cobertura léxica y ganó su propio
examen con el check relajado, pero perdió puntos por seguimiento de instrucciones
(nombre truncado, formato de entrega) y por errores aritméticos como examinador.
