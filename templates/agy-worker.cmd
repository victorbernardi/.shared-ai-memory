@echo off
REM Perfil WORKER para Antigravity CLI (agy)
REM Execucao de tasks delimitadas em sandbox seguro
echo [AGY :: WORKER] Iniciando em modo executor de tasks (Sandbox seguro)...
agy --mode=accept-edits --sandbox %*
