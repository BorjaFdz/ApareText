# Build Script para ApareText
# Este script compila tanto el backend como el frontend y crea el instalador

Write-Host "`n==============================================================" -ForegroundColor Cyan
Write-Host "       ApareText - Build System                          " -ForegroundColor Cyan
Write-Host "==============================================================`n" -ForegroundColor Cyan

# Función para calcular tamaño de directorio
function Get-DirectorySize {
    param([string]$path)
    if (Test-Path $path) {
        return (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    }
    return 0
}

# Configuración de rutas
# NOTA: El build se hace SIEMPRE en OneDrive para mantener el repositorio limpio
# - Repositorio (_Repostitorios/ApareText/): contiene SOLO código fuente
# - Build directory (OneDrive/Escritorio/ApareText-Build/): contiene artifacts compilados
$desktopPath = "$env:USERPROFILE\OneDrive\Escritorio"
$buildDir = "$desktopPath\ApareText-Build"
$repoPath = Split-Path -Parent $PSScriptRoot
$dbFile = "aparetext.db"
$dbFile = "aparetext.db"

Write-Host "Build directory: $buildDir" -ForegroundColor Gray
Write-Host "Repository: $repoPath`n" -ForegroundColor Gray

# Mostrar tamaño inicial del directorio de build
$initialSize = Get-DirectorySize $buildDir
Write-Host "Initial build directory size: $([math]::Round($initialSize, 2)) MB`n" -ForegroundColor Gray

# Paso 0: Preparar directorio de build
Write-Host "[0/4] Preparando directorio de build..." -ForegroundColor Yellow

# Verificar espacio en disco
$desktopDrive = (Get-Item $desktopPath).PSDrive.Name
$freeSpace = (Get-PSDrive $desktopDrive).Free / 1GB
Write-Host "   Espacio disponible en $($desktopDrive): $([math]::Round($freeSpace, 2)) GB" -ForegroundColor Gray

if ($freeSpace -lt 2) {
    Write-Host "`n[ERROR] Espacio insuficiente en disco. Se necesitan al menos 2GB libres." -ForegroundColor Red
    exit 1
}

# Crear directorio si no existe
if (-not (Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
}

# Preservar base de datos si existe
$dbSource = "$buildDir\$dbFile"
$dbTemp = "$env:TEMP\aparetext_build_db.bak"

if (Test-Path $dbSource) {
    Write-Host "   Preserving database..." -ForegroundColor Gray
    Copy-Item $dbSource $dbTemp -Force
}

# Limpieza agresiva del directorio de build
Write-Host "   Cleaning build directory..." -ForegroundColor Gray
Get-ChildItem $buildDir -Exclude ".git" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Limpiar archivos temporales del sistema
Write-Host "   Cleaning temporary files..." -ForegroundColor Gray
Get-ChildItem "$env:TEMP" -Filter "aparetext_*" -File | Remove-Item -Force -ErrorAction SilentlyContinue

# Copiar SOLO código fuente y dependencias necesarias (no .git, no artifacts previos)
Write-Host "   Copying source code to build directory..." -ForegroundColor Gray
$excludeDirs = @(".git", "node_modules", "__pycache__", ".pytest_cache", "htmlcov")
$excludeFiles = @("*.pyc", "*.pyo", "*.log", ".DS_Store", "Thumbs.db")

# Copiar estructura de directorios primero
Get-ChildItem $repoPath -Directory | Where-Object { $_.Name -notin $excludeDirs } | ForEach-Object {
    Copy-Item $_.FullName $buildDir -Recurse -Force
}

# Copiar archivos individuales excluyendo los no deseados
Get-ChildItem $repoPath -File | Where-Object { $_.Name -notin $excludeFiles } | ForEach-Object {
    Copy-Item $_.FullName $buildDir -Force
}

# Restaurar base de datos
if (Test-Path $dbTemp) {
    Write-Host "   Restoring database..." -ForegroundColor Gray
    Copy-Item $dbTemp $dbSource -Force
    Remove-Item $dbTemp -Force
}

# Cambiar al directorio de build
Set-Location $buildDir

Write-Host "[OK] Build directory prepared`n" -ForegroundColor Green
Write-Host "[1/4] Compilando backend con PyInstaller..." -ForegroundColor Yellow

# Usar Python del sistema o del entorno virtual local
$pythonExe = "python"
if (Test-Path "venv\Scripts\python.exe") {
    $pythonExe = ".\venv\Scripts\python.exe"
} elseif (Test-Path "C:\Users\bfern\_Repostitorios\ApareText\venv\Scripts\python.exe") {
    $pythonExe = "C:\Users\bfern\_Repostitorios\ApareText\venv\Scripts\python.exe"
}

& $pythonExe -m PyInstaller aparetext_server.spec --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Error compilando backend" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Backend compilado exitosamente`n" -ForegroundColor Green

# Verificar que el exe existe
if (-not (Test-Path "dist\ApareText-Server-v2.exe")) {
    Write-Host "[ERROR] No se encontro dist\ApareText-Server-v2.exe" -ForegroundColor Red
    exit 1
}

# Mostrar tamaño
$size = (Get-Item "dist\ApareText-Server-v2.exe").Length / 1MB
Write-Host "   Tamaño del backend: $([math]::Round($size, 2)) MB`n" -ForegroundColor White

# Paso 2: Instalar dependencias de Electron (si es necesario)
Write-Host "[2/4] Verificando dependencias de Electron..." -ForegroundColor Yellow
Set-Location electron-app

if (-not (Test-Path "node_modules")) {
    Write-Host "   Instalando node_modules..." -ForegroundColor Gray
    npm install
}

Write-Host "[OK] Dependencias verificadas`n" -ForegroundColor Green

# Paso 3: Compilar Electron
Write-Host "[3/4] Compilando aplicacion Electron..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar 3-5 minutos)`n" -ForegroundColor Gray

npm run build:win

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Error compilando Electron" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# Paso 4: Limpiar archivos innecesarios
Write-Host "[4/4] Limpiando archivos innecesarios..." -ForegroundColor Yellow

# Preservar instaladores antes de limpiar
$installerDir = "$buildDir\Installers"
if (-not (Test-Path $installerDir)) {
    New-Item -ItemType Directory -Path $installerDir -Force | Out-Null
}

# Mover instaladores a directorio seguro
if (Test-Path "electron-app\output") {
    Write-Host "   Preserving installers..." -ForegroundColor Gray
    Get-ChildItem "electron-app\output" -Filter "*.exe" | ForEach-Object {
        $destPath = Join-Path $installerDir $_.Name
        Copy-Item $_.FullName $destPath -Force
        Write-Host "     Preserved: $($_.Name)" -ForegroundColor Gray
    }
}

# Eliminar directorios de build acumulados
$cleanDirs = @("electron-app\build", "electron-app\build-output", "electron-app\dist-out", "electron-app\dist2", "electron-app\output", "build", "dist")
foreach ($dir in $cleanDirs) {
    if (Test-Path $dir) {
        $size = (Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "   Removing $dir ($([math]::Round($size, 2)) MB)..." -ForegroundColor Gray
        Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Limpiar archivos temporales de Python
Write-Host "   Cleaning Python cache files..." -ForegroundColor Gray
Get-ChildItem . -Include "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem . -Include "*.pyc", "*.pyo", "*.pyd" -Recurse -File | Remove-Item -Force -ErrorAction SilentlyContinue

# Limpiar archivos temporales de Node.js
Write-Host "   Cleaning Node.js cache..." -ForegroundColor Gray
if (Test-Path "electron-app\node_modules\.cache") {
    Remove-Item "electron-app\node_modules\.cache" -Recurse -Force -ErrorAction SilentlyContinue
}

# Limpiar archivos de log
Write-Host "   Cleaning log files..." -ForegroundColor Gray
Get-ChildItem . -Include "*.log" -Recurse -File | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "[OK] Cleanup completed`n" -ForegroundColor Green

# Mostrar estadísticas finales
$finalSize = Get-DirectorySize $buildDir
$savedSpace = $initialSize - $finalSize
Write-Host "Build directory size: $([math]::Round($finalSize, 2)) MB (saved $([math]::Round($savedSpace, 2)) MB)`n" -ForegroundColor Green

# Resumen
Write-Host "`n==============================================================" -ForegroundColor Green
Write-Host "       BUILD COMPLETADO EXITOSAMENTE                      " -ForegroundColor Green
Write-Host "==============================================================`n" -ForegroundColor Green

Write-Host "Archivos generados:`n" -ForegroundColor Cyan

# Listar instaladores generados
if (Test-Path $installerDir) {
    Get-ChildItem $installerDir -File | Where-Object { $_.Extension -in ".exe", ".zip" } | ForEach-Object {
        $sizeOutput = $_.Length / 1MB
        Write-Host "   [OK] $($_.Name)" -ForegroundColor White
        Write-Host "      Tamaño: $([math]::Round($sizeOutput, 2)) MB" -ForegroundColor Gray
        Write-Host "      Ubicacion: $($_.FullName)`n" -ForegroundColor Gray
    }
}

Write-Host "ApareText esta listo para distribuir!`n" -ForegroundColor Green
Write-Host "Para instalar, ejecuta el archivo .exe desde la carpeta Installers`n" -ForegroundColor White
