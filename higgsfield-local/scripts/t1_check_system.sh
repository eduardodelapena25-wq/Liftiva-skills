#!/usr/bin/env bash
# T1 — Diagnóstico del sistema (solo lectura, no cambia nada).
# Correr EN LA MÁQUINA con Mint y pegar la salida completa en notes/BITACORA.md:
#   bash scripts/t1_check_system.sh 2>&1 | tee notes/t1_output.txt

set -u

section() { printf '\n=== %s ===\n' "$1"; }

section "OS / Kernel"
cat /etc/os-release 2>/dev/null | grep -E '^(NAME|VERSION)=' || true
uname -r

section "GPUs detectadas (lspci)"
lspci | grep -iE 'vga|display|3d' || echo "lspci no disponible"

section "Driver amdgpu cargado"
lsmod | grep -E '^amdgpu' || echo "amdgpu NO cargado"

section "Dispositivos DRM / render nodes"
ls -l /dev/dri/ 2>/dev/null || echo "sin /dev/dri"

section "Grupos del usuario (necesita: render, video)"
id
groups | tr ' ' '\n' | grep -E '^(render|video)$' >/dev/null \
  && echo "OK: usuario en render/video" \
  || echo "FALTA: sudo usermod -aG render,video \$USER  (y re-login)"

section "RAM"
free -h

section "VRAM reportada por el kernel"
for d in /sys/class/drm/card*/device; do
  [ -f "$d/mem_info_vram_total" ] || continue
  name=$(cat "$d/product_name" 2>/dev/null || basename "$(dirname "$d")")
  vram=$(cat "$d/mem_info_vram_total")
  echo "$d → $((vram / 1024 / 1024)) MiB ($name)"
done

section "¿ROCm ya instalado?"
command -v rocminfo >/dev/null && rocminfo | grep -E 'Name:.*gfx' | sort -u \
  || echo "rocminfo no encontrado (ROCm no instalado aún — esperado antes de T2)"
command -v rocm-smi >/dev/null && rocm-smi --showproductname 2>/dev/null || true
ls -d /opt/rocm* 2>/dev/null || echo "sin /opt/rocm*"

section "¿Mesa / Vulkan? (referencia)"
command -v glxinfo >/dev/null && glxinfo -B 2>/dev/null | grep -E 'OpenGL (vendor|renderer|version)' \
  || echo "glxinfo no instalado (opcional: sudo apt install mesa-utils)"

section "ffmpeg y encoders VAAPI/VCN disponibles"
command -v ffmpeg >/dev/null \
  && { ffmpeg -version 2>/dev/null | head -1; ffmpeg -hide_banner -encoders 2>/dev/null | grep -E 'vaapi|amf' || echo "sin encoders vaapi/amf listados"; } \
  || echo "ffmpeg no instalado (sudo apt install ffmpeg)"

section "Python"
python3 --version 2>/dev/null || echo "sin python3"
command -v pip3 >/dev/null && pip3 --version || true

section "Espacio en disco"
df -h / /home 2>/dev/null | sort -u

printf '\n=== FIN T1 — pega toda esta salida en notes/BITACORA.md ===\n'
