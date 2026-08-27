$taskName = "InstallDockerDesktop"
$installerPath = "$env:USERPROFILE\Downloads\DockerDesktopInstaller.exe"
$action = "cmd.exe /c `"$installerPath`" install --quiet --accept-license --backend=wsl-2"

# Remove tarefa anterior se existir
schtasks /delete /tn $taskName /f 2>$null

# Cria tarefa agendada com privilégios máximos (HIGHEST)
schtasks /create /tn $taskName /tr "$installerPath install --quiet --accept-license --backend=wsl-2" /sc ONCE /st 23:59 /rl HIGHEST /f

# Executa imediatamente a tarefa agendada
schtasks /run /tn $taskName
