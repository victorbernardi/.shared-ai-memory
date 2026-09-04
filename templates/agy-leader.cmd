@echo off
REM Perfil LEADER para Antigravity CLI (agy)
REM Sessao principal com aprovacao automatica total de permissoes (YOLO)
echo [AGY :: LEADER] Iniciando em modo Lider / YOLO (Aprovacao total de permissoes)...
agy --dangerously-skip-permissions %*
