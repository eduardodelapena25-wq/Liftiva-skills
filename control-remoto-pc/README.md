# Control remoto de la PC desde la laptop (Sunshine + Moonlight)

Objetivo: trabajar acostado/cómodo desde la laptop (18") controlando la PC de
escritorio con sus dos monitores, con latencia casi nula, como si estuvieras
sentado frente a ella.

> **¿Cómo usar esto con Claude Code?** Abre Claude Code en este repositorio y
> escribe `/control-remoto-pc` (o simplemente dile "guíame con el control
> remoto de mi PC"). Claude leerá esta guía y te irá llevando paso a paso,
> preguntándote en qué máquina estás y verificando cada paso contigo.

## Resumen de la solución

| Máquina | Programa | Rol |
|---|---|---|
| PC de escritorio (2 monitores) | **Sunshine** | Servidor: transmite pantalla, recibe teclado/mouse |
| Laptop 18" | **Moonlight** | Cliente: ves y controlas la PC |

Ambos son gratuitos y open source. En red local (tu casa) la fluidez es
prácticamente idéntica a estar frente a la PC.

## Instalación automática

En cada máquina, abre **PowerShell como administrador** (clic derecho al menú
inicio → "Terminal (administrador)") y ejecuta el script que corresponde:

### En la PC de escritorio

```powershell
irm https://raw.githubusercontent.com/eduardodelapena25-wq/Liftiva-skills/claude/remote-pc-control-setup-tnp3hh/control-remoto-pc/instalar-pc.ps1 | iex
```

O si ya clonaste el repositorio:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\control-remoto-pc\instalar-pc.ps1
```

El script instala Sunshine con `winget`, lo deja iniciando con Windows y abre
la página de configuración.

### En la laptop

```powershell
irm https://raw.githubusercontent.com/eduardodelapena25-wq/Liftiva-skills/claude/remote-pc-control-setup-tnp3hh/control-remoto-pc/instalar-laptop.ps1 | iex
```

O desde el repositorio clonado:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\control-remoto-pc\instalar-laptop.ps1
```

El script instala Moonlight y lo deja listo para emparejar.

## Emparejar la laptop con la PC (una sola vez, ~2 minutos)

1. **En la laptop**: abre Moonlight. Si ambas máquinas están en la misma red
   WiFi/ethernet, la PC aparece sola en la lista. Haz clic en ella → te
   muestra un **PIN de 4 dígitos**.
2. **En la PC**: abre la página de Sunshine (`https://localhost:47990`).
   - La primera vez el navegador dice "conexión no segura": es normal en
     localhost, dale **Continuar**.
   - La primera vez te pide crear **usuario y contraseña**: apúntalos.
   - Ve a la pestaña **PIN**, escribe el PIN que muestra la laptop y un nombre
     (ej. "Laptop") → **Send**.
3. Listo. Quedan emparejadas para siempre.

## Uso diario

- En Moonlight haz clic en **Desktop** → ya estás controlando la PC completa:
  teclado, mouse y audio.
- Salir de la sesión: `Ctrl + Alt + Shift + Q`.
- En Moonlight → **Settings**, pon la resolución **igual a la de tu laptop**
  y 60 fps (o 120 si tu laptop lo soporta) para máxima nitidez.

## Manejar los dos monitores desde la laptop de 18"

En 18 pulgadas lo cómodo es ver **un monitor a la vez** y cambiar con un clic:

1. En la PC, abre Sunshine (`https://localhost:47990`) → **Configuration →
   Audio/Video** → campo **Display/Output name**: ahí eliges qué monitor se
   transmite (`\\.\DISPLAY1` o `\\.\DISPLAY2` en Windows).
2. Truco más cómodo — crea dos "aplicaciones" en Sunshine:
   - Pestaña **Applications** → **Add New** → nombre `Monitor 1`, y en
     opciones de salida el display 1. Repite con `Monitor 2` y el display 2.
   - En Moonlight aparecerán "Monitor 1" y "Monitor 2" como si fueran juegos:
     eliges a cuál conectarte con un clic.
3. Dentro de la sesión también puedes mover ventanas del monitor que no ves
   al que sí ves con `Win + Shift + flecha izquierda/derecha`.

## Dos ajustes que hacen gran diferencia

1. **PC por cable ethernet al router** (la laptop puede ir por WiFi). Elimina
   prácticamente todo el lag.
2. **Wake-on-LAN** para encender la PC desde el sillón sin levantarte:
   - En la BIOS de la PC: activa "Wake on LAN" / "Power On by PCI-E".
   - En Windows: Administrador de dispositivos → tu adaptador de red →
     Propiedades → **Administración de energía** → marca "Permitir que este
     dispositivo reactive el equipo".
   - En Moonlight, al hacer clic en una PC apagada/suspendida aparece la
     opción de despertarla.

## Problemas comunes

| Síntoma | Solución |
|---|---|
| La PC no aparece en Moonlight | Verifica que ambas están en la **misma red**. En la PC revisa que Sunshine esté corriendo (icono en la bandeja). El instalador de Sunshine ya crea las reglas de firewall; si las bloqueaste, reinstala o permite `sunshine.exe` en el Firewall de Windows. |
| Pantalla negra al conectar | En Sunshine → Audio/Video, selecciona explícitamente el monitor. Si la PC no tiene monitor encendido, conéctale un "dummy plug" HDMI o deja un monitor encendido. |
| Se ve borroso | Sube la resolución en Moonlight a la nativa de la laptop y el bitrate a 40–80 Mbps (Settings). |
| Lag o cortes | Conecta la PC por ethernet; acércate al router con la laptop; baja a 60 fps. |
| `winget` no existe | Instala "Instalador de aplicación" desde Microsoft Store, o descarga los instaladores a mano: Sunshine (github.com/LizardByte/Sunshine/releases) y Moonlight (moonlight-stream.org). |

## Archivos de esta carpeta

```
README.md            # esta guía
instalar-pc.ps1      # instala y configura Sunshine en la PC de escritorio
instalar-laptop.ps1  # instala Moonlight en la laptop
```
