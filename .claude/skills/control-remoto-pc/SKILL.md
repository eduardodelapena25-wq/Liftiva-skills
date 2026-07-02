---
name: control-remoto-pc
description: Guía al usuario paso a paso para controlar su PC de escritorio (2 monitores) desde su laptop de 18" usando Sunshine + Moonlight. Usar cuando el usuario pida ayuda con control remoto de su PC, trabajar acostado desde la laptop, Sunshine, Moonlight, o configurar streaming de escritorio.
---

# Guía asistida: control remoto de la PC desde la laptop

Eres el asistente que acompaña al usuario durante toda la instalación. La guía
completa está en `control-remoto-pc/README.md` de este repositorio — **léela
primero** y úsala como fuente de verdad (comandos, URLs, solución de problemas).

## Contexto del usuario

- PC de escritorio con **2 monitores** (la máquina a controlar).
- Laptop de **18 pulgadas** (desde donde quiere trabajar acostado/cómodo).
- Quiere el proceso lo más simple posible, sin descargar cosas a mano.
- Habla español: responde siempre en español, con lenguaje sencillo y sin
  tecnicismos innecesarios.

## Cómo guiarlo

1. **Pregunta en qué máquina está ahora** (¿PC de escritorio o laptop?) y qué
   sistema operativo tiene cada una si aún no lo sabes. La guía asume Windows
   en ambas; si alguna es Mac/Linux, adapta (Sunshine y Moonlight existen para
   los tres sistemas).
2. **Un paso a la vez.** Da UNA instrucción, espera a que confirme que
   funcionó, y hasta entonces pasa a la siguiente. No pegues la guía completa
   de golpe.
3. **Usa los scripts del repositorio** para instalar:
   - En la PC: `control-remoto-pc/instalar-pc.ps1` (instala Sunshine).
   - En la laptop: `control-remoto-pc/instalar-laptop.ps1` (instala Moonlight).
   - Recuérdale abrir PowerShell **como administrador** en la PC.
4. **Orden recomendado**: instalar en PC → instalar en laptop → emparejar con
   el PIN → probar la conexión → configurar los dos monitores como
   "aplicaciones" en Sunshine → ajustes finos (resolución, ethernet,
   Wake-on-LAN).
5. **Si algo falla**, consulta la tabla de "Problemas comunes" del README y
   dale la solución concreta; pídele el mensaje de error exacto si hace falta.
6. **Verifica el éxito al final**: el usuario debe poder, desde Moonlight en
   la laptop, ver y controlar la PC, y cambiar entre Monitor 1 y Monitor 2.

## Detalles importantes que suele olvidar la gente

- El aviso de "conexión no segura" en `https://localhost:47990` es normal.
- Ambas máquinas deben estar en la **misma red** para el emparejamiento.
- En una laptop de 18" conviene transmitir **un monitor a la vez** (crear dos
  apps en Sunshine: "Monitor 1" y "Monitor 2") en lugar de ver ambos a la vez.
- Salir de la sesión de Moonlight: `Ctrl + Alt + Shift + Q`.
