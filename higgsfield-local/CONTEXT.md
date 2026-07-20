# CONTEXTO DEL PROYECTO: "HIGGSFIELD LOCAL" EN AMD + LINUX MINT

> Documento de contexto / prompt de handoff.
> Objetivo: montar un pipeline local de generación de imagen y video con IA,
> en hardware AMD de gama media, para producir imágenes HD y ensamblar clips
> cortos hasta un video final en 1080p, sin depender de servicios cloud de pago.
>
> Puedes pegar este documento como contexto inicial para un agente (Claude Code,
> Codex, etc.) o usarlo como referencia técnica propia. Todo lo que dice aquí
> ya fue filtrado por realismo: no promete calidad que el hardware no da.

---

## 0. ROL Y MODO DE TRABAJO (si esto es un prompt para un agente)

Actúa como un ingeniero de ML/infra especializado en generación local con
difusión sobre hardware AMD (ROCm) en Linux. Tu trabajo es ayudarme a montar,
depurar y operar el pipeline descrito abajo. Prioridades, en orden:

1. **Honestidad técnica sobre optimismo.** Si algo no es viable en este
   hardware, dilo claro y ofrece la alternativa realista. No inventes que 8GB
   de VRAM rinden como 24GB.
2. **Estabilidad antes que lo último.** Prefiere versiones y rutas probadas
   (ej. ROCm 6.4.1) sobre lo más nuevo si lo nuevo crashea en gfx1032.
3. **Comandos copy-paste.** Cuando des instalación o workflows, dámelos listos
   para copiar, con rutas concretas y variables de entorno explícitas.
4. **Divide el problema.** Imagen y video son dos tracks distintos con
   distintos niveles de viabilidad. No los mezcles en una sola promesa.
5. **Español mexicano casual.** Términos técnicos en inglés como es natural.

---

## 1. OBJETIVO REAL DEL PROYECTO

Quiero replicar localmente el tipo de resultado que da Higgsfield, con estas
metas concretas:

- Generar **imágenes HD/1080p** de buena calidad, fotorrealistas, offline.
- Generar **clips de video cortos** a partir de esas imágenes (image-to-video).
- **Escalar cada clip** y **encadenarlos/juntarlos** en un editor hasta armar
  un video final en **1080p**.
- Iterar mucho: "probar de todo", generar varias tomas y quedarme con las
  buenas. Es un flujo de tanda y paciencia, no de un prompt mágico.

Estrategia central: **no pelear contra el límite de VRAM, sino rodearlo.**
Generar en pedazos (stills → clips cortos → upscale → ensamble) en vez de
intentar generar un 1080p largo de un solo golpe.

---

## 2. QUÉ ES HIGGSFIELD (PARA CALIBRAR EXPECTATIVAS)

Higgsfield **no es un solo modelo ni un solo motor**. Es un orquestador / hub
que combina varios modelos en un mismo workspace y enruta cada petición al que
mejor le queda (model routing). Se divide en:

- **Modelos propios:** Soul / Soul 2 (modelo estrella, enfocado a moda,
  retrato y estética editorial; buen manejo de piel, telas e iluminación
  intencional) y Soul ID (consistencia de identidad de personaje).
- **Modelos de terceros integrados:** Nano Banana Pro (Google), Seedream
  (ByteDance), FLUX, GPT Image, y para video Kling, Seedance, Veo, Sora, Wan.

**Implicación clave:** buena parte de lo que impresiona de Higgsfield —sobre
todo el video— corre en modelos cloud propietarios de gama alta. Esos NO tienen
pesos abiertos y NO se pueden correr local. Lo replicable local es el lado de
imagen con modelos abiertos, y una fracción limitada del video.

---

## 3. HARDWARE DISPONIBLE (UNA SOLA MÁQUINA)

| Componente | Detalle | Notas para IA |
|---|---|---|
| GPU dedicada | **AMD Radeon RX 6600** | RDNA2, **gfx1032**, **8GB VRAM**. Es el cuello de botella real. |
| APU / CPU | **Ryzen 7 5700G** | 8 núcleos / 16 hilos. Trae iGPU integrada. |
| iGPU | **Radeon Vega 8** | gfx90c. Usa RAM del sistema (memoria compartida/GTT), NO tiene VRAM propia. |
| RAM | **32 GB** | Es el "pool extra" real vía offloading. Subir a 64GB ayudaría más que la iGPU. |
| OS | **Linux Mint Cinnamon** | Basado en Ubuntu. **Mejor terreno para AMD** (ROCm es principalmente tecnología de Linux). |

**Nota importante sobre la iGPU:** NO se puede "sumar" la Vega 8 + la RX 6600
en una sola GPU con VRAM combinada. El pooling de VRAM entre GPUs heterogéneas
para una misma generación no es viable aquí (no hay NVLink, distinta
arquitectura). Además la Vega 8 es débil y está limitada por el ancho de banda
de la DDR4; usarla para difusión sería MÁS LENTO que la RX 6600 sola. Su valor
está en post-proceso paralelo (ver sección 8), no en generación.

---

## 4. VEREDICTO DE REALISMO (LO QUE SÍ Y LO QUE NO)

| Meta | ¿Realista en este hardware? | Detalle |
|---|---|---|
| Imágenes HD/1080p local | ✅ Sí | SDXL nativo a 1024px + upscale. La brecha local vs cloud se cerró mucho en 2026. |
| Look editorial exacto de Soul | ⚠️ Parcial | Te acercas con LoRAs de CivitAI + ControlNet, pero no sale idéntico "de fábrica". |
| Consistencia de personaje (tipo Soul ID) | ⚠️ Parcial | Se puede entrenar un LoRA propio, pero en 8GB es lento y apretado. |
| Clips de video cortos (i2v) | ✅ Sí (con recortes) | 480p, ~5s, lentos. Calidad tipo cloud de hace 6-12 meses. |
| Video calidad Kling/Sora/Veo | ❌ No | Esa calidad ES cloud tope de gama. No corre local, punto. |
| Video 720p buena calidad | ❌ No en 8GB | Requiere mínimo ~16GB VRAM. |
| Video 1080p/10s+ nativo | ❌ No en 8GB | Requiere 24-32GB VRAM. Se llega a 1080p por upscale, no por generación directa. |
| FramePack (video largo low-VRAM) | ❌ No en AMD | Requiere NVIDIA RTX 30/40/50 (FP16/BF16). No hay soporte AMD/Intel. |

**Resumen honesto:** se puede montar ~70-80% del **lado de imágenes** de
Higgsfield local. El video de calidad y la plataforma completa (orquestación,
campañas, brand kits), no. Para video con calidad real, la ruta honesta es
híbrida (imagen local + video por API cloud) o hardware con más VRAM.

---

## 5. STACK DE SOFTWARE

### 5.1 Base
- **ComfyUI** — el default de producción en 2026 (basado en nodos, soporte más
  rápido para modelos nuevos). Alternativa más simple de arranque: **Forge**
  (pensado para poca VRAM).
- **PyTorch con wheels de ROCm** (no CUDA; esto es AMD).
- **ffmpeg** para ensamble y encode.
- Editor de video nativo en Mint: **Kdenlive** o **Shotcut**.

### 5.2 El detalle crítico de tu GPU (gfx1032)
La RX 6600 es **gfx1032**, que oficialmente ROCm NO soporta. Además, el soporte
nativo experimental de AMD en ComfyUI es solo para RDNA 3/3.5/4 — la serie 6000
(RDNA2) queda fuera de esa ruta directa. Dos formas de resolverlo:

**Opción A — ROCm estable + override (recomendada por estabilidad):**
- Instalar **ROCm 6.4.1** (ver gotcha abajo).
- Exportar `HSA_OVERRIDE_GFX_VERSION=10.3.0` para que la gfx1032 se haga pasar
  por gfx1030 (RX 6800/6900). El override entre tarjetas de la misma generación
  es seguro.

**Opción B — builds semi-oficiales gfx103X (más limpia si funciona):**
- Usar los nightly de ROCm/PyTorch del repo **TheRock** de AMD, compilados
  específicamente para la serie gfx103X. No necesitan el override porque están
  hechos para tu arquitectura. Hay instaladores comunitarios (patientx) que
  autodetectan la GPU e instalan ROCm, PyTorch, triton, etc.

### 5.3 ⚠️ GOTCHA QUE TE AHORRA HORAS
Hay una **regresión sin resolver**: **ROCm 6.4.3+ y toda la línea 7.2.x
crashean con SIGSEGV** justo en gfx1031/gfx1032 al usar el override.
→ **Quédate en ROCm 6.4.1**, o usa los builds gfx103X nativos (Opción B).

### 5.4 Setup de sistema
- Meter tu usuario a los grupos `render` y `video`.
- Para resoluciones >512px en ROCm: usar **tiled VAE encode/decode** (el VAE
  normal puede caer a tiled automático pero es lento; mejor los nodos tiled).
- Flags útiles de offload en ComfyUI: `--lowvram`, `--async-offload N`,
  `--use-quad-cross-attention` (o `--use-pytorch-cross-attention` según versión).

---

## 6. MODELOS RECOMENDADOS

### 6.1 Imagen (lo que tu RX 6600 SÍ hace bien)
| Modelo | Por qué | Notas |
|---|---|---|
| **SDXL** | Sweet spot para 8GB, el ecosistema más grande de LoRAs y ControlNet. Licencia limpia para comercial. | Empezar aquí. Formato `.safetensors` (más estable que GGUF en AMD). Nativo 1024×1024. |
| **FLUX.2 Klein 4B** | Modelo nuevo (ene 2026), ~2.6GB en Q4, genera en 4 pasos, cabe holgado en 8GB, Apache 2.0. | Para probar; ojo con GGUF en AMD (ver caveat). |
| **Z-Image Turbo (nf4)** | Corre en RDNA2 y usa la mitad de VRAM que un GGUF Q8. | Buena opción cuando andes justo de memoria. |
| **FLUX.1 dev/schnell (GGUF)** | Look clásico FLUX. | dev = licencia NO comercial; schnell = Apache 2.0. Usar Q4_K_S (~6.8GB) + `--lowvram`. |

### 6.2 Video (limitado pero posible)
| Modelo | Por qué | Notas |
|---|---|---|
| **LTX-Video 2.3** | El más rápido y de menor barrera; corre en 8GB+ con FP8 + tiling. Modo image-to-video. | **Tu mejor opción de video en AMD 8GB.** |
| **Wan 2.2 1.3B (GGUF)** | Cabe en 8GB (~8.19GB sin trucos). | Calidad menor que la 14B. Clip 5s/480p ≈ 4-6 min en una 4060; tu AMD irá más lento. |

### 6.3 Post-proceso
| Herramienta | Función |
|---|---|
| **RealESRGAN (4x)** | Upscale espacial: de 480p sube hacia 1080p+. |
| **RIFE** | Interpolación de frames: sube de 24 a 60fps, suaviza el movimiento. |
| **ffmpeg** | Corte, concatenación y encode final. |

> Dato: RealESRGAN + RIFE juntos duplican la calidad percibida sin generar
> frames nuevos y a bajo costo de cómputo. Suben calidad *percibida*; NO inventan
> detalle real ni arreglan artefactos de motion.

### 6.4 ⚠️ CAVEAT DE GGUF EN AMD
En AMD han reportado un bug donde los archivos **GGUF subutilizan la GPU** y se
vuelve lentísimo (tipo cientos de segundos por iteración). Por eso: arranca con
**SDXL en `.safetensors`**, y prueba GGUF solo con cautela.

---

## 7. EL PIPELINE POR ETAPAS (EL CORAZÓN DEL PROYECTO)

Esta es la estrategia de "generar en pedazos y ensamblar". Es exactamente cómo
se hacen los videos largos con IA, incluso con modelos cloud (los clips topan en
5-20s y lo largo se arma en editor).

```
[1] KEYFRAMES / STILLS BASE
    SDXL en ComfyUI → imágenes HD de alta calidad.
    Son las anclas de calidad. Un still por cada toma que quieras.
    Aquí la RX 6600 rinde bien.
        │
        ▼
[2] IMAGE-TO-VIDEO (i2v)
    LTX-Video 2.3 (i2v) → convierte cada still en un clip corto (~5s, 480p).
    La calidad del still se hereda al primer frame del clip.
        │
        ▼
[3] UPSCALE POR CLIP
    RealESRGAN 4x → cada clip de 480p sube hacia 1080p.
    (Este es el paso de "que cada video suba".)
        │
        ▼
[4] INTERPOLACIÓN
    RIFE → sube de 24 a 60fps, suaviza el movimiento.
        │
        ▼
[5] ENSAMBLE FINAL
    ffmpeg (o Kdenlive/Shotcut) → une todos los clips ya escalados.
    Salida: secuencia final en 1080p.
```

### 7.1 Trucos de consistencia (para que no se vea como pedazos sueltos)
Lo más difícil de juntar clips es que no brinque el look entre tomas:

- **Mismo LoRA de personaje (o mismo seed)** en todos los stills base → el look
  no cambia entre tomas.
- **Encadenar el último frame de un clip como imagen inicial del siguiente**
  (i2v encadenado) → el movimiento fluye entre secciones en vez de cortar seco.
  Es justo la técnica para extender clips en 8GB.

### 7.2 Sobre generación "en partes" (staging / chunking)
La intuición de generar la base y correr el proceso por partes es correcta y
es ingeniería real. PERO ojo con qué resuelve:

- **Resuelve:** el problema de VRAM y de DURACIÓN (cabe el modelo, clips más
  largos).
- **NO resuelve:** el problema de CALIDAD. El techo lo pone el modelo, no la
  memoria. Hacer chunks de un modelo mediano no lo convierte en Kling.
- **FramePack** es la herramienta estrella de esta técnica (genera por
  secciones con VRAM constante sin importar la duración, ancla cada sección a un
  frame de alta calidad con muestreo anti-drift). PERO requiere NVIDIA RTX
  30/40/50 → **no aplica a tu RX 6600.**

---

## 8. USO DEL HARDWARE: DIVISIÓN DE LABOR (NO POOLING)

No se junta la VRAM. En vez de eso, se reparte el trabajo en pipeline para
exprimir toda la máquina:

| Recurso | Rol asignado |
|---|---|
| **RX 6600 (8GB)** | Generación pesada: SDXL, i2v LTX. Su chamba exclusiva. |
| **RAM 32GB** | Pool extra REAL vía offloading. Los pesos se transmiten desde RAM a la GPU (`--lowvram`, `--async-offload`). Este es el "sumar" que importa. |
| **CPU 5700G (8 núcleos)** | Pasos no-difusión: rutas por CPU de RealESRGAN/RIFE, y ensamble con ffmpeg. |
| **iGPU Vega 8 (encoder VCN)** | Encode por hardware H.264/H.265/AV1 del clip final, liberando a la RX 6600. |

**Pipeline paralelo:** mientras la RX 6600 genera el clip B, el CPU + iGPU
escalan y codifican el clip A. Así se usa todo, pero como línea de producción,
no como una GPU gigante.

**Mejora futura de mayor impacto (dentro de lo barato):** subir la RAM a **64GB**
ayuda más al offloading que cualquier cosa que haga la iGPU.

---

## 9. EXPECTATIVAS DE RENDIMIENTO (SIN ENDULZAR)

- SDXL 1024px en la RX 6600: **decenas de segundos** por imagen (no los ~6s de
  una tarjeta tope de gama). Perfectamente usable para trabajar.
- Clip de video 5s/480p: **varios minutos** por clip. Trabajo de tanda.
- Motion complejo (cambios de escena, muchos sujetos): sale pobre en modelos
  locales. Funciona mejor para motion simple / movimiento de cámara.
- El resultado final: un **1080p armado por ti, offline y a $0/imagen**, con
  calidad decente — NO calidad cinemática Higgsfield.

---

## 10. RUTA HÍBRIDA (RECOMENDADA PARA VIDEO DE CALIDAD)

Si el video de calidad importa de verdad, la jugada honesta es partir el
problema:

1. **Imágenes → local** (RX 6600 + Mint). Sí vale la pena hoy.
2. **Video → API cloud** de modelos abiertos (Wan, LTX) o de paga (Kling,
   Seedance). Sale mucho más barato que comprar hardware de 24GB solo para eso.

Alternativa "fierro": si quieres video local en serio, el piso real es una
**NVIDIA de 16GB (mínimo) o 24GB** — no una AMD de 8. La NVIDIA además desbloquea
CUDA nativo (cero traductores) y FramePack.

---

## 11. LICENCIAS (PARA NO METERTE EN BRONCAS SI ES COMERCIAL)

- **SDXL:** licencia limpia para uso comercial.
- **FLUX.2 Klein 4B:** Apache 2.0 (comercial OK).
- **FLUX.1 schnell:** Apache 2.0 (comercial OK).
- **FLUX.1 dev:** **NO comercial.**
- Revisar caso por caso los LoRAs de CivitAI (cada uno trae su propia licencia).

---

## 12. RIESGOS Y PUNTOS DE FALLA CONOCIDOS

1. **SIGSEGV en ROCm 6.4.3+/7.2.x con gfx1032** → usar 6.4.1 o builds gfx103X.
2. **GGUF subutiliza la GPU en AMD** → preferir `.safetensors`.
3. **VAE OOM en >512px** → usar nodos tiled VAE.
4. **iGPU reportada como VRAM dedicada** (bug ComfyUI en APUs) → puede causar
   presión de memoria; forzar modo shared/UMA si aparece.
5. **Expectativa de calidad de video** → el mayor riesgo es de frustración, no
   técnico. Tener claro el veredicto de la sección 4.

---

## 13. PLAN DE EJECUCIÓN (TAREAS EN ORDEN)

- [ ] **T1.** Confirmar versión de Mint y estado actual de drivers amdgpu.
- [ ] **T2.** Instalar ROCm 6.4.1 (Opción A) o builds gfx103X (Opción B).
- [ ] **T3.** Configurar entorno: grupos `render`/`video`, exportar
      `HSA_OVERRIDE_GFX_VERSION=10.3.0` (si Opción A), verificar que PyTorch ve
      la GPU (`torch.cuda.is_available()` en ROCm reporta True).
- [ ] **T4.** Instalar ComfyUI + dependencias, confirmar autodetección de GPU.
- [ ] **T5.** Descargar SDXL + un upscaler (4x-UltraSharp / RealESRGAN) + RIFE.
- [ ] **T6.** Armar y probar workflow de **imagen**: SDXL 1024 → upscale a 1080p.
- [ ] **T7.** Descargar LTX-Video 2.3, armar workflow **i2v** (still → clip 480p).
- [ ] **T8.** Armar cadena de post: RealESRGAN + RIFE por clip.
- [ ] **T9.** Script de **ensamble** con ffmpeg (concat + encode, idealmente por
      VCN de la iGPU).
- [ ] **T10.** Definir convención de consistencia (LoRA/seed fijo, encadenado de
      último frame).
- [ ] **T11.** Prueba end-to-end: 3 stills → 3 clips → upscale → ensamble 1080p.
- [ ] **T12.** (Opcional) Evaluar ruta híbrida de video por API para tomas que
      necesiten calidad alta.

---

## 14. GLOSARIO RÁPIDO

- **VRAM:** memoria de la GPU. El límite duro aquí (8GB).
- **ROCm:** el "CUDA de AMD". Principalmente Linux.
- **gfx1032 / gfx1030 / gfx90c:** nombres de arquitectura ISA de las GPUs AMD
  (RX 6600 / RX 6800-6900 / Vega 8 iGPU).
- **HSA_OVERRIDE_GFX_VERSION:** variable que hace que una GPU no soportada se
  presente como otra compatible.
- **i2v / t2v:** image-to-video / text-to-video.
- **offloading:** transmitir pesos del modelo desde RAM a VRAM bajo demanda para
  correr modelos que no caben enteros en la GPU.
- **GGUF / safetensors:** formatos de pesos. GGUF cuantizado ahorra VRAM pero da
  problemas en AMD; safetensors es más estable aquí.
- **RIFE / RealESRGAN:** interpolación de frames / upscaling de imagen-video.
- **VCN:** el encoder de video por hardware de las GPUs AMD.

---

FIN DEL CONTEXTO.
