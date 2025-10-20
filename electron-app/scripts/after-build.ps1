# Script que se ejecuta después del build de ApareText
# Limpia archivos temporales y verifica que el build fue exitoso

Write-Host "🧹 Iniciando limpieza posterior al build..." -ForegroundColor Cyan

$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $currentDir
$distDir = Join-Path $projectDir "dist"

# 1. Verificar que los archivos del build existen
Write-Host "🔍 Verificando archivos del build..." -ForegroundColor Yellow
$setupFiles = Get-ChildItem -Path $distDir -Filter "*Setup*.exe" -ErrorAction SilentlyContinue
$portableFiles = Get-ChildItem -Path $distDir -Filter "*portable*.exe" -ErrorAction SilentlyContinue

if ($setupFiles.Count -gt 0) {
    Write-Host "✅ Encontrado archivo de instalación: $($setupFiles[0].Name)" -ForegroundColor Green
} else {
    Write-Host "❌ No se encontró archivo de instalación" -ForegroundColor Red
}

if ($portableFiles.Count -gt 0) {
    Write-Host "✅ Encontrado archivo portable: $($portableFiles[0].Name)" -ForegroundColor Green
} else {
    Write-Host "❌ No se encontró archivo portable" -ForegroundColor Red
}

# 2. Limpiar archivos temporales
Write-Host "🗑️  Limpiando archivos temporales..." -ForegroundColor Yellow
$tempFiles = @(
    "*.tmp",
    "*.temp",
    "*.log",
    "nsis-*.tmp"
)

foreach ($pattern in $tempFiles) {
    $files = Get-ChildItem -Path $distDir -Filter $pattern -Recurse -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction Stop
            Write-Host "🗑️  Eliminado: $($file.Name)" -ForegroundColor Gray
        } catch {
            # Ignorar errores en limpieza de temporales
        }
    }
}

# 3. Verificar tamaño de archivos
Write-Host "📏 Verificando tamaños de archivos..." -ForegroundColor Yellow
$exeFiles = Get-ChildItem -Path $distDir -Filter "*.exe" -ErrorAction SilentlyContinue
foreach ($file in $exeFiles) {
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    Write-Host "📄 $($file.Name): ${sizeMB}MB" -ForegroundColor Cyan
}

# 4. Crear archivo de información del build
$buildInfo = @{
    BuildDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    SetupFile = if ($setupFiles.Count -gt 0) { $setupFiles[0].Name } else { "No encontrado" }
    PortableFile = if ($portableFiles.Count -gt 0) { $portableFiles[0].Name } else { "No encontrado" }
    TotalFiles = (Get-ChildItem -Path $distDir -File -ErrorAction SilentlyContinue).Count
}

$buildInfo | ConvertTo-Json | Out-File -FilePath (Join-Path $distDir "build-info.json") -Encoding UTF8
Write-Host "Informacion del build guardada en build-info.json" -ForegroundColor Green

Write-Host "Limpieza posterior al build completada" -ForegroundColor Green