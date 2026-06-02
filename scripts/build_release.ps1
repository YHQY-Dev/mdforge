#Requires -Version 5.1
<#
.SYNOPSIS
  Build MdForge release artifacts: portable zip + Windows installer.

.DESCRIPTION
  Uses uv run --with pyinstaller (project venv + deps), then packages:
    - release/MdForge-<version>-portable-win64.zip  (免安装版)
    - release/MdForge-<version>-setup-win64.exe      (安装版, Inno Setup)
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

function Get-AppVersion {
    $init = Join-Path $ProjectRoot "src\mdforge\__init__.py"
    if (-not (Test-Path $init)) { return "0.0.0" }
    $match = Select-String -Path $init -Pattern '__version__\s*=\s*"([^"]+)"' | Select-Object -First 1
    if ($match) { return $match.Matches[0].Groups[1].Value }
    return "0.0.0"
}

function Find-InnoSetupCompiler {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) { return $path }
    }
    return $null
}

$Version = Get-AppVersion
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$DistDir = Join-Path $ProjectRoot "dist\MdForge"
$ReleaseDir = Join-Path $ProjectRoot "release"
$PortableZip = Join-Path $ReleaseDir "MdForge-$Version-portable-win64.zip"
$SetupExe = Join-Path $ReleaseDir "MdForge-$Version-setup-win64.exe"

Write-Host "==> MdForge release build v$Version" -ForegroundColor Cyan

Write-Host "==> uv sync" -ForegroundColor Yellow
uv sync

if (-not (Test-Path $VenvPython)) {
    throw "Project venv not found at $VenvPython. Run 'uv sync' first."
}

Write-Host "==> Clean previous build outputs" -ForegroundColor Yellow
foreach ($path in @(
        (Join-Path $ProjectRoot "build"),
        (Join-Path $ProjectRoot "dist"),
        $ReleaseDir
    )) {
    if (Test-Path $path) { Remove-Item $path -Recurse -Force }
}
New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null

Write-Host "==> PyInstaller (uv run --with pyinstaller)" -ForegroundColor Yellow
uv run --with pyinstaller pyinstaller mdforge.spec --noconfirm --clean

if (-not (Test-Path (Join-Path $DistDir "MdForge.exe"))) {
    throw "PyInstaller output missing: $(Join-Path $DistDir 'MdForge.exe')"
}

Write-Host "==> Portable zip" -ForegroundColor Yellow
if (Test-Path $PortableZip) { Remove-Item $PortableZip -Force }
Compress-Archive -Path (Join-Path $DistDir "*") -DestinationPath $PortableZip -CompressionLevel Optimal
Write-Host "    $PortableZip"

Write-Host "==> Windows installer (Inno Setup)" -ForegroundColor Yellow
$Iscc = Find-InnoSetupCompiler
if ($null -eq $Iscc) {
    Write-Warning @"
Inno Setup 6 not found. Install from https://jrsoftware.org/isinfo.php
Then re-run: .\scripts\build_release.ps1

Portable zip is ready; installer was skipped.
"@
    exit 0
}

$Iss = Join-Path $ProjectRoot "installer\mdforge.iss"
& $Iscc $Iss
if (-not (Test-Path $SetupExe)) {
    throw "Inno Setup did not produce: $SetupExe"
}
Write-Host "    $SetupExe"

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "  Portable : $PortableZip"
Write-Host "  Installer: $SetupExe"
