# Bitácora del proyecto

Registro de avance por tarea. Cada entrada: fecha, qué se hizo, salida relevante,
decisiones tomadas y broncas encontradas.

---

## 2026-07-20 — Arranque del proyecto

- Se creó la estructura del proyecto y se guardó el contexto completo en
  `CONTEXT.md` (fuente de verdad).
- Se creó `scripts/t1_check_system.sh` para la tarea T1 (diagnóstico de solo
  lectura: OS, driver amdgpu, grupos, VRAM, ROCm, ffmpeg/VAAPI, disco).
- **Siguiente paso:** correr T1 en la máquina con Mint y pegar la salida aquí:

  ```bash
  bash scripts/t1_check_system.sh 2>&1 | tee notes/t1_output.txt
  ```

### Decisiones abiertas

- [ ] Opción A (ROCm 6.4.1 + `HSA_OVERRIDE_GFX_VERSION=10.3.0`) vs Opción B
      (builds gfx103X de TheRock). Se decide después de ver la salida de T1.

---

## T1 — Diagnóstico del sistema

*(pendiente — pegar aquí la salida de `t1_check_system.sh`)*
