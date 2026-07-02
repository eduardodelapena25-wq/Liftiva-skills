# Instala Moonlight (cliente) en la laptop.
# Ejecutar en PowerShell (no requiere administrador si winget lo permite,
# pero como administrador evita cualquier traba).

$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '=== Instalador de Moonlight (laptop) ===' -ForegroundColor Cyan
Write-Host ''

# 1. Verificar winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host 'ERROR: winget no esta disponible.' -ForegroundColor Red
    Write-Host 'Instala "Instalador de aplicacion" desde Microsoft Store y reintenta,'
    Write-Host 'o descarga Moonlight manualmente: https://moonlight-stream.org'
    exit 1
}

# 2. Instalar Moonlight
Write-Host '[1/2] Instalando Moonlight con winget...' -ForegroundColor Yellow
winget install --id MoonlightGameStreamingProject.Moonlight --accept-source-agreements --accept-package-agreements --silent
if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) {
    # -1978335189 = ya estaba instalado
    Write-Host "winget termino con codigo $LASTEXITCODE. Si fallo, instala manualmente desde:" -ForegroundColor Red
    Write-Host 'https://moonlight-stream.org'
    exit 1
}
Write-Host '      Moonlight instalado.' -ForegroundColor Green

# 3. Abrir Moonlight
Write-Host '[2/2] Abriendo Moonlight...' -ForegroundColor Yellow
$rutas = @(
    "$env:ProgramFiles\Moonlight Game Streaming\Moonlight.exe",
    "$env:LOCALAPPDATA\Programs\Moonlight Game Streaming\Moonlight.exe"
)
$exe = $rutas | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($exe) { Start-Process $exe } else { Write-Host '      Abrelo desde el menu inicio: "Moonlight".' -ForegroundColor Yellow }

Write-Host ''
Write-Host '=== Listo. Siguientes pasos ===' -ForegroundColor Cyan
Write-Host '1. Asegurate de que la PC de escritorio ya tiene Sunshine instalado'
Write-Host '   (script instalar-pc.ps1) y que ambas estan en la misma red.'
Write-Host '2. En Moonlight, tu PC aparece sola en la lista. Haz clic en ella.'
Write-Host '3. Te mostrara un PIN de 4 digitos: escribelo en la PC, en'
Write-Host '   https://localhost:47990 -> pestana PIN -> Send.'
Write-Host '4. Ya emparejadas: clic en "Desktop" y a trabajar desde el sillon.'
Write-Host '   Para salir de la sesion: Ctrl + Alt + Shift + Q'
