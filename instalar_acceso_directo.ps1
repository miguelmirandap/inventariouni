$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$venvPip = Join-Path $PSScriptRoot ".venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Creando entorno virtual..."
    c:/python313/python.exe -m venv .venv
}

Write-Host "Instalando dependencias..."
& $venvPip install -r requirements.txt

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Inventario Cafeteria.lnk"
$targetPath = Join-Path $PSScriptRoot "iniciar_inventario.bat"
$iconPath = Join-Path $PSScriptRoot "assets\icon_taza_check.ico"

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $PSScriptRoot
if (Test-Path $iconPath) {
    $shortcut.IconLocation = $iconPath
} else {
    $shortcut.IconLocation = "$env:SystemRoot\System32\SHELL32.dll,220"
}
$shortcut.Save()

Write-Host "Instalacion completada."
Write-Host "Acceso directo creado en: $shortcutPath"
Write-Host "Ahora abre 'Inventario Cafeteria' desde el escritorio."
