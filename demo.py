#!/usr/bin/env python3
"""Demostración rápida del motor de leads con mensajes de ejemplo."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "implementations" / "fable5"))
from classifier import classify

EJEMPLOS = [
    {"nombre": "Marcela", "canal": "whatsapp",
     "mensaje": "Hola, tengo una estética y estoy perdiendo citas porque no "
                "alcanzo a contestar el WhatsApp. ¿Me pueden automatizar eso? "
                "Tengo como 15 mil de presupuesto."},
    {"nombre": "", "canal": "formulario",
     "mensaje": "Quisiera saber más de sus servicios y cómo trabajan."},
    {"nombre": "Cristina", "canal": "email",
     "mensaje": "Le ofrecemos posicionamiento SEO garantizado en 7 días, "
                "promoción por hoy."},
]

for lead in EJEMPLOS:
    print("=" * 72)
    print(f"Lead ({lead['canal']}): {lead['mensaje']}")
    print("-" * 72)
    print(json.dumps(classify(lead), indent=2, ensure_ascii=False))
