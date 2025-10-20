# Limpieza agresiva para build de ApareText

Write-Host 'Iniciando limpieza agresiva...' -ForegroundColor Cyan

# Desactivar Windows Defender
try {
    Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
    Write-Host 'Defender desactivado' -ForegroundColor Green
} catch {
    Write-Host 'No se pudo desactivar Defender' -ForegroundColor Yellow
}

# Matar procesos
taskkill /F /IM 'ApareText*.exe' /T 2>$null
taskkill /F /IM 'electron.exe' /T 2>$null
taskkill /F /IM 'node.exe' /T 2>$null

Start-Sleep -Seconds 2

# Limpiar directorios
$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $currentDir

$dirs = @('dist', 'build')
foreach ($dir in $dirs) {
    $path = Join-Path $projectDir $dir
    if (Test-Path $path) {
        Write-Host "Limpiando $dir..." -ForegroundColor Yellow
        
        # Intentar múltiples métodos
        try {
            Remove-Item $path -Recurse -Force -ErrorAction Stop
            Write-Host 'OK con Remove-Item' -ForegroundColor Green
        } catch {
            try {
                cmd /c "rd /s /q "$path"" 2>$null
                Write-Host 'OK con CMD' -ForegroundColor Green
            } catch {
                Write-Host "Fallo limpieza $dir" -ForegroundColor Red
            }
        }
    }
    
    # Crear directorio
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory $path -Force | Out-Null
        Write-Host "Directorio $dir creado" -ForegroundColor Green
    }
}

# Reactivar Defender
try {
    Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue
    Write-Host 'Defender reactivado' -ForegroundColor Green
} catch {
    Write-Host 'No se pudo reactivar Defender' -ForegroundColor Yellow
}

Write-Host 'Limpieza completada' -ForegroundColor Green
