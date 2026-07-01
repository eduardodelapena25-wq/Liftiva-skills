#!/usr/bin/env python3
"""Evalúa implementaciones del motor de leads (SPEC.md) contra eval/leads_eval.json.

Uso:
    python3 run_eval.py                # evalúa todas las carpetas en implementations/
    python3 run_eval.py fable5 opus    # evalúa solo las indicadas
    python3 run_eval.py -v fable5      # muestra el detalle de cada caso fallado

Cada implementación es una carpeta implementations/<nombre>/ con un classifier.py
que expone classify(lead: dict) -> dict.

Puntuación por caso (100 pts): intención 40, urgencia 20, puntaje exacto 25,
respuesta 15. El total del set es el promedio de todos los casos.
"""

import importlib.util
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).parent
PESOS = {"intencion": 40, "urgencia": 20, "puntaje": 25, "respuesta": 15}

KW_RESPUESTA = {
    "diagnostico": "diagnostico",
    "proyecto": "propuesta",
    "implementacion": "llamada",
    "soporte": "revisar",
}


def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def check_respuesta(lead, intencion_esperada, respuesta):
    """Verifica los requisitos de la sección 4 de SPEC.md."""
    if not isinstance(respuesta, str):
        return False
    if intencion_esperada == "otro":
        return respuesta.strip() == ""
    r = norm(respuesta)
    if not r.strip():
        return False
    if lead["nombre"] and norm(lead["nombre"]) not in r:
        return False
    return KW_RESPUESTA[intencion_esperada] in r


def cargar_classify(carpeta):
    ruta = carpeta / "classifier.py"
    if not ruta.exists():
        return None, f"no existe {ruta}"
    spec = importlib.util.spec_from_file_location(f"clf_{carpeta.name}", ruta)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        return None, f"error al importar: {e}"
    if not hasattr(mod, "classify"):
        return None, "no define classify()"
    return mod.classify, None


def evaluar(nombre, classify, casos, verbose=False):
    total = 0.0
    aciertos = {k: 0 for k in PESOS}
    fallas = []

    for caso in casos:
        lead, esp = caso["lead"], caso["esperado"]
        try:
            out = classify(dict(lead))
        except Exception as e:
            fallas.append((caso, {"error": repr(e)}, list(PESOS)))
            continue

        malos = []
        if out.get("intencion") != esp["intencion"]:
            malos.append("intencion")
        if out.get("urgencia") != esp["urgencia"]:
            malos.append("urgencia")
        if out.get("puntaje") != esp["puntaje"]:
            malos.append("puntaje")
        if not check_respuesta(lead, esp["intencion"], out.get("respuesta", "")):
            malos.append("respuesta")

        for k in PESOS:
            if k not in malos:
                aciertos[k] += 1
        total += sum(v for k, v in PESOS.items() if k not in malos)
        if malos:
            fallas.append((caso, out, malos))

    n = len(casos)
    print(f"\n=== {nombre} ===")
    print(f"  Puntuación total : {total / n:6.1f} / 100")
    for k in PESOS:
        print(f"  {k:<10} : {aciertos[k]}/{n} ({100 * aciertos[k] / n:.0f}%)")
    print(f"  Casos perfectos  : {n - len(fallas)}/{n}")

    if fallas:
        etiquetas = ", ".join("#{}({})".format(c["id"], ",".join(m)) for c, _, m in fallas)
        print(f"  Casos con fallas : {etiquetas}")
        if verbose:
            for caso, out, malos in fallas:
                print(f"\n  --- caso #{caso['id']} [{caso['nivel']}] falló {malos}")
                print(f"      mensaje : {caso['lead']['mensaje']!r}")
                print(f"      esperado: {caso['esperado']}")
                print(f"      obtenido: { {k: out.get(k) for k in ('intencion', 'urgencia', 'puntaje')} }")
                if "respuesta" in malos:
                    print(f"      respuesta: {out.get('respuesta')!r}")
    return total / n


def main():
    argv = sys.argv[1:]
    verbose = "-v" in argv
    argv = [a for a in argv if a != "-v"]
    ruta_eval = RAIZ / "eval" / "leads_eval.json"
    if "--eval" in argv:
        i = argv.index("--eval")
        ruta_eval = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = argv
    print(f"[set de evaluación: {ruta_eval.name}]")
    casos = json.loads(ruta_eval.read_text(encoding="utf-8"))

    base = RAIZ / "implementations"
    carpetas = [base / a for a in args] if args else sorted(
        p for p in base.iterdir() if p.is_dir())

    resultados = {}
    for carpeta in carpetas:
        classify, err = cargar_classify(carpeta)
        if err:
            print(f"\n=== {carpeta.name} ===\n  OMITIDA: {err}")
            continue
        resultados[carpeta.name] = evaluar(carpeta.name, classify, casos, verbose)

    if len(resultados) > 1:
        print("\n=== Comparativa ===")
        for nombre, score in sorted(resultados.items(), key=lambda x: -x[1]):
            print(f"  {nombre:<12} {score:6.1f} / 100")


if __name__ == "__main__":
    main()
