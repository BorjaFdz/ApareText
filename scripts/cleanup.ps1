# Cleanup Script for ApareText Build Artifacts
# Run this after closing all ApareText instances and restarting if needed

Write-Host "🧹 ApareText Build Artifacts Cleanup" -ForegroundColor Cyan
Write-Host "=====================================`n" -ForegroundColor Cyan

$repoPath = Split-Path -Parent $PSScriptRoot
Set-Location $repoPath

Write-Host "Repository: $repoPath`n" -ForegroundColor Gray

# Build artifacts to remove
$artifacts = @(
    "electron-app\build",
    "electron-app\build-output",
    "electron-app\dist",
    "electron-app\dist-out",
    "electron-app\dist2",
    "electron-app\output",
    "electron-app\output2",
    "build",
    "dist",
    "dist2",
    "htmlcov"
)

$totalFreed = 0
$removedCount = 0

foreach ($artifact in $artifacts) {
    if (Test-Path $artifact) {
        try {
            $size = (Get-ChildItem $artifact -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
            Remove-Item $artifact -Recurse -Force -ErrorAction Stop
            Write-Host "✓ Removed $artifact ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
            $totalFreed += $size
            $removedCount++
        }
        catch {
            Write-Host "✗ Failed to remove $artifact (still locked)" -ForegroundColor Red
        }
    }
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "Directories removed: $removedCount" -ForegroundColor White
Write-Host "Space freed: $([math]::Round($totalFreed, 2)) MB" -ForegroundColor White
Write-Host "`nRepository is now clean! 🎉" -ForegroundColor Green