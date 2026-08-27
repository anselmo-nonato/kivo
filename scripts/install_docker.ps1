$url = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$output = "$env:USERPROFILE\Downloads\DockerDesktopInstaller.exe"

if (-not (Test-Path $output)) {
    Write-Host "Baixando Docker Desktop Installer..."
    Invoke-WebRequest -Uri $url -OutFile $output
}

Write-Host "Iniciando instalador com elevação de Administrador..."
Start-Process -FilePath $output -Verb RunAs
