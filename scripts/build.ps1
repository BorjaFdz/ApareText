# Build Script para ApareText
# Este script compila tanto el backend como el frontend y crea el instalador

Write-Host "`n==============================================================" -ForegroundColor Cyan
Write-Host "       ApareText - Build System                          " -ForegroundColor Cyan
Write-Host "==============================================================`n" -ForegroundColor Cyan

# Paso 1: Compilar Backend
Write-Host "[1/3] Compilando backend con PyInstaller..." -ForegroundColor Yellow
C:/Users/bfern/_Repostitorios/ApareText/venv/Scripts/python.exe -m PyInstaller aparetext_server.spec --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Error compilando backend" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Backend compilado exitosamente`n" -ForegroundColor Green

# Verificar que el exe existe
if (-not (Test-Path "dist\ApareText-Server.exe")) {
    Write-Host "[ERROR] No se encontro dist\ApareText-Server.exe" -ForegroundColor Red
    exit 1
}

# Mostrar tamaño
$size = (Get-Item "dist\ApareText-Server.exe").Length / 1MB
Write-Host "   Tamaño del backend: $([math]::Round($size, 2)) MB`n" -ForegroundColor White

# Paso 2: Instalar dependencias de Electron (si es necesario)
Write-Host "[2/3] Verificando dependencias de Electron..." -ForegroundColor Yellow
Set-Location electron-app

if (-not (Test-Path "node_modules")) {
    Write-Host "   Instalando node_modules..." -ForegroundColor Gray
    npm install
}

Write-Host "[OK] Dependencias verificadas`n" -ForegroundColor Green

# Paso 3: Compilar Electron
Write-Host "[3/3] Compilando aplicacion Electron..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar 3-5 minutos)`n" -ForegroundColor Gray

npm run build:win

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Error compilando Electron" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# Resumen
Write-Host "`n==============================================================" -ForegroundColor Green
Write-Host "       BUILD COMPLETADO EXITOSAMENTE                      " -ForegroundColor Green
Write-Host "==============================================================`n" -ForegroundColor Green

Write-Host "Archivos generados:`n" -ForegroundColor Cyan

# Listar instaladores generados
if (Test-Path "electron-app\dist") {
    Get-ChildItem "electron-app\dist" -File | Where-Object { $_.Extension -in ".exe", ".zip" } | ForEach-Object {
        $sizeOutput = $_.Length / 1MB
        Write-Host "   [OK] $($_.Name)" -ForegroundColor White
        Write-Host "      Tamaño: $([math]::Round($sizeOutput, 2)) MB" -ForegroundColor Gray
        Write-Host "      Ubicacion: $($_.FullName)`n" -ForegroundColor Gray
    }
}

Write-Host "ApareText esta listo para distribuir!`n" -ForegroundColor Green
Write-Host "Para instalar, ejecuta el archivo .exe desde electron-app\dist\`n" -ForegroundColor White
