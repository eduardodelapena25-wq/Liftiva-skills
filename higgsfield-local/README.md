# Higgsfield Local — AMD RX 6600 + Linux Mint

Pipeline local de generación de imagen y video con IA en hardware AMD de gama
media. Imágenes HD con SDXL, clips cortos con LTX-Video, upscale + interpolación,
y ensamble final en 1080p con ffmpeg. Todo offline, $0/imagen.

**📄 Fuente de verdad:** [`CONTEXT.md`](CONTEXT.md) — todo el contexto técnico,
veredicto de realismo, gotchas conocidos y plan de ejecución. Léelo antes de
tocar cualquier cosa.

## Estructura

```
higgsfield-local/
├── CONTEXT.md      # Documento de contexto completo (handoff / prompt de agente)
├── README.md       # Este archivo
├── scripts/        # Scripts del pipeline (diagnóstico, setup, post, ensamble)
├── workflows/      # Workflows JSON de ComfyUI (imagen, i2v)
└── notes/          # Bitácora de avance y hallazgos por tarea
```

## El pipeline en una línea

```
SDXL stills 1024px → LTX-Video i2v (5s/480p) → RealESRGAN 4x → RIFE 60fps → ffmpeg concat → 1080p final
```

## Lo esencial que no se te puede olvidar

- **RX 6600 = gfx1032, 8GB.** ROCm no la soporta oficialmente → `HSA_OVERRIDE_GFX_VERSION=10.3.0` (Opción A) o builds gfx103X de TheRock (Opción B).
- **ROCm 6.4.1, no más nuevo.** 6.4.3+ y 7.2.x hacen SIGSEGV en gfx1032 con el override.
- **`.safetensors` > GGUF en AMD.** GGUF puede subutilizar la GPU.
- **Tiled VAE** para todo lo que pase de 512px.
- **La VRAM no se suma con la iGPU.** La Vega 8 solo sirve para encode VCN; el "pool extra" real es la RAM (32GB) vía offloading.

## Estado de tareas

Ver plan completo en `CONTEXT.md` sección 13. Avance registrado en
[`notes/BITACORA.md`](notes/BITACORA.md).

| Tarea | Descripción | Estado |
|---|---|---|
| T1 | Confirmar Mint + drivers amdgpu | ⬜ pendiente — correr `scripts/t1_check_system.sh` en la máquina |
| T2 | Instalar ROCm 6.4.1 o builds gfx103X | ⬜ pendiente |
| T3 | Entorno: grupos, override, PyTorch ve GPU | ⬜ pendiente |
| T4 | ComfyUI + dependencias | ⬜ pendiente |
| T5 | Descargar SDXL + upscaler + RIFE | ⬜ pendiente |
| T6 | Workflow imagen: SDXL 1024 → 1080p | ⬜ pendiente |
| T7 | LTX-Video 2.3 + workflow i2v | ⬜ pendiente |
| T8 | Cadena post: RealESRGAN + RIFE por clip | ⬜ pendiente |
| T9 | Script ensamble ffmpeg (VCN si se puede) | ⬜ pendiente |
| T10 | Convención de consistencia (seed/LoRA, encadenado) | ⬜ pendiente |
| T11 | Prueba end-to-end: 3 stills → 1080p | ⬜ pendiente |
| T12 | (Opcional) Evaluar ruta híbrida por API | ⬜ pendiente |
