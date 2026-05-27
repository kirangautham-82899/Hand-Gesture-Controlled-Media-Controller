param(
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

Write-Host "Building desktop bundle with PyInstaller..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist\HandGestureMediaController") { Remove-Item -Recurse -Force "dist\HandGestureMediaController" }

pyinstaller --noconfirm --windowed --name HandGestureMediaController --paths src scripts\run_gui.py

Write-Host "Building installer with Inno Setup..."
$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
    throw "Inno Setup 6 not found. Install from https://jrsoftware.org/isdl.php and re-run."
}

& $iscc "/DMyAppVersion=$Version" "installer\HandGestureMediaController.iss"

Write-Host "Done. Installer output:"
Get-ChildItem "dist_installer"
