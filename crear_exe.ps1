$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$venvPip = Join-Path $PSScriptRoot ".venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual..."
    c:/python313/python.exe -m venv .venv
}

Write-Host "Instalando dependencias de empaquetado..."
& $venvPip install -r requirements.txt
& $venvPip install pyinstaller

$iconPath = Join-Path $PSScriptRoot "assets\icon_taza_check.ico"

Write-Host "Generando ejecutable..."
if (Test-Path $iconPath) {
    & $venvPython -m PyInstaller --noconfirm --onefile --name InventarioCafeteria --icon $iconPath --add-data "templates;templates" --add-data "static;static" app_web.py
} else {
    & $venvPython -m PyInstaller --noconfirm --onefile --name InventarioCafeteria --add-data "templates;templates" --add-data "static;static" app_web.py
}

Write-Host "Listo. Ejecutable en: dist\InventarioCafeteria.exe"
