# Script para configurar o agendamento do Dashboard Inova
$TaskName = "Inova_Wave9_Daily_Update"
$PythonPath = "python.exe"
$ScriptPath = "c:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave9_Deployment_OnePage.py"
$WorkingDirectory = "c:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos"

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDirectory
$Trigger = New-ScheduledTaskTrigger -Daily -At 8am
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName $TaskName -Description "Atualização diária do Dashboard Wave 9 Inova" -Settings $Settings -Force
