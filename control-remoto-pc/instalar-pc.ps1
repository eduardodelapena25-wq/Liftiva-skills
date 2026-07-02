# Instala Sunshine (servidor de streaming) en la PC de escritorio.
# Ejecutar en PowerShell COMO ADMINISTRADOR.

$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '=== Instalador de Sunshine (PC de escritorio) ===' -ForegroundColor Cyan
Write-Host ''

# 1. Verificar que somos administrador
$esAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $esAdmin) {
    Write-Host 'ERROR: Abre PowerShell como ADMINISTRADOR y vuelve a ejecutar.' -ForegroundColor Red
    Write-Host '(Clic derecho al menu inicio -> Terminal (administrador))'
    exit 1
}

# 2. Verificar winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host 'ERROR: winget no esta disponible.' -ForegroundColor Red
    Write-Host 'Instala "Instalador de aplicacion" desde Microsoft Store y reintenta,'
    Write-Host 'o descarga Sunshine manualmente: https://github.com/LizardByte/Sunshine/releases'
    exit 1
}

# 3. Instalar Sunshine (el instalador crea el servicio y las reglas de firewall)
Write-Host '[1/3] Instalando Sunshine con winget...' -ForegroundColor Yellow
winget install --id LizardByte.Sunshine --accept-source-agreements --accept-package-agreements --silent
if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) {
    # -1978335189 = ya estaba instalado
    Write-Host "winget termino con codigo $LASTEXITCODE. Si fallo, instala manualmente desde:" -ForegroundColor Red
    Write-Host 'https://github.com/LizardByte/Sunshine/releases'
    exit 1
}
Write-Host '      Sunshine instalado.' -ForegroundColor Green

# 4. Asegurar que el servicio arranque con Windows
Write-Host '[2/3] Configurando inicio automatico...' -ForegroundColor Yellow
$svc = Get-Service -Name 'SunshineService' -ErrorAction SilentlyContinue
if ($svc) {
    Set-Service -Name 'SunshineService' -StartupType Automatic
    if ($svc.Status -ne 'Running') { Start-Service -Name 'SunshineService' }
    Write-Host '      Servicio de Sunshine activo y en inicio automatico.' -ForegroundColor Green
} else {
    Write-Host '      No encontre el servicio; abre Sunshine desde el menu inicio una vez.' -ForegroundColor Yellow
}

# 5. Mostrar la IP local (util para emparejar) y abrir la pagina de configuracion
Write-Host '[3/3] Abriendo pagina de configuracion...' -ForegroundColor Yellow
$ips = Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -ne '127.0.0.1' } |
    Select-Object -ExpandProperty IPAddress
Start-Process 'https://localhost:47990'

Write-Host ''
Write-Host '=== Listo. Siguientes pasos ===' -ForegroundColor Cyan
Write-Host '1. En la pagina que se abrio (avisa "no segura": dale Continuar, es normal'
Write-Host '   en localhost), crea tu usuario y contrasena la primera vez.'
Write-Host '2. En la LAPTOP instala Moonlight (script instalar-laptop.ps1).'
Write-Host '3. En Moonlight haz clic en esta PC: te dara un PIN de 4 digitos.'
Write-Host '4. Regresa a esta pagina -> pestana PIN -> escribe el PIN -> Send.'
Write-Host ''
Write-Host ("IP de esta PC en tu red: " + ($ips -join ', ')) -ForegroundColor Green
Write-Host '(Normalmente Moonlight la detecta sola; usa la IP solo si no aparece.)'
