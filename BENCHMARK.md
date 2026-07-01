# Benchmark: Fable 5 vs Opus — Motor de leads Liftiva

Protocolo para comparar dos modelos en la **misma tarea, con la misma especificación,
calificados por el mismo evaluador automático**. La tarea es real para Liftiva:
implementar el clasificador de leads descrito en `SPEC.md`.

## Cómo funciona la comparación

1. Ambos modelos reciben **solo** el contenido de `SPEC.md` (nunca el set de
   evaluación `eval/leads_eval.json` — ese es el examen sorpresa).
2. Cada modelo entrega un `classifier.py` en un solo intento (one-shot).
3. `run_eval.py` califica ambos con los mismos 36 casos y pesos:
   intención 40%, urgencia 20%, puntaje exacto 25%, respuesta 15%.

## Pasos para correr la comparación

### 1. Pídele la implementación a Opus

Abre una sesión nueva con Opus (por ejemplo Claude Opus 4.8 en claude.ai o
Claude Code con `/model opus`) y pégale exactamente esto, seguido del contenido
completo de `SPEC.md`:

> Implementa la siguiente especificación en un solo archivo `classifier.py`
> (Python 3.11, solo librería estándar, sin red ni modelos de lenguaje).
> Entrégalo en un solo intento, completo y listo para ejecutar. No hagas
> preguntas; resuelve las ambigüedades con tu mejor criterio. Especificación:

### 2. Guarda su respuesta

Copia el código que entregue (tal cual, sin corregirle nada) a:

```
implementations/opus/classifier.py
```

### 3. Corre la evaluación

```bash
python3 run_eval.py
```

Imprime la puntuación de cada implementación y una tabla comparativa al final.
Con `-v` muestra el detalle de cada caso fallado:

```bash
python3 run_eval.py -v opus
```

## Métricas a registrar

| Métrica | Cómo se mide |
|---|---|
| **Puntuación del eval** (principal) | Salida de `run_eval.py` (0–100) |
| Casos perfectos | "Casos perfectos: N/36" en la salida |
| Casos difíciles | Fallas en los casos marcados `"nivel": "dificil"` (13, 19, 21, 23, 24, 25, 28, 31, 33, 35) |
| One-shot limpio | ¿El código corrió a la primera sin errores de sintaxis/importación? |
| Tiempo | Minutos desde que pegas el prompt hasta tener el archivo |
| Tamaño | Líneas de código (`wc -l classifier.py`) |
| Legibilidad | Tu juicio: ¿lo entiendes y podrías mantenerlo? |

## Resultados (comparación ya ejecutada — ver INFORME.md)

La comparación se corrió con evaluación cruzada: un agente Opus implementó la spec
one-shot (`implementations/opus/classifier.py`, guardado sin correcciones) y otro
agente Opus redactó un segundo examen desde la spec
(`eval/leads_eval_opus.json`; 2 de sus 20 puntajes traían errores aritméticos del
propio Opus — original en `eval/leads_eval_opus_original.json`).

| Set | Fable 5 | Opus |
|---|---|---|
| Examen de Fable 5 (36 casos) | **100.0** | 87.8 |
| Examen de Opus (20 casos) | **80.0** | 79.0 |
| **Combinado (56 casos)** | **92.9** | **84.6** |

Detalle, análisis de sensibilidad y hallazgos cualitativos en `INFORME.md`.
Para reproducir: `python3 run_eval.py` y
`python3 run_eval.py --eval eval/leads_eval_opus.json`.

## Nota de imparcialidad (importante)

El set de evaluación lo escribió **el mismo modelo que hizo la implementación de
referencia** (Fable 5), en esta misma sesión. Aunque la implementación se escribió
*antes* que el eval y ambas se derivan solo de `SPEC.md`, existe una ventaja
inherente: el autor del examen difícilmente reprueba su propio examen.

Para una comparación realmente ciega, agrega casos que ninguno de los dos modelos
haya visto — idealmente **mensajes reales de tu WhatsApp Business** — al final de
`eval/leads_eval.json` con este formato (etiqueta tú mismo lo esperado siguiendo
`SPEC.md`):

```json
{"id": 37, "nivel": "real", "lead": {"nombre": "...", "canal": "whatsapp", "mensaje": "..."},
 "esperado": {"intencion": "...", "urgencia": "...", "puntaje": 0}}
```

Esos casos "reales" son los que más pesan para decidir: miden qué tan bien
generalizó cada modelo más allá de los ejemplos de la especificación.
