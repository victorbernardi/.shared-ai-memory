<#
.SYNOPSIS
    Perfis de Execução do Antigravity CLI (agy): Worker e Leader.

.DESCRIPTION
    - agy-worker (agyw): Modo executor de tasks delimitadas (Orca / feat/project_lead), com sandbox ativo e restrito.
    - agy-leader (agyl): Modo sessão principal / líder (YOLO), com aprovação automática total de permissões (--dangerously-skip-permissions).
#>

function agy-worker {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$ArgsList
    )
    Write-Host "[AGY :: WORKER] Iniciando modo executor de tasks (Sandbox seguro)..." -ForegroundColor Cyan
    & agy --mode=accept-edits --sandbox @ArgsList
}

function agy-leader {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$ArgsList
    )
    Write-Host "[AGY :: LEADER] Iniciando modo Líder / YOLO (Aprovação total de permissões)..." -ForegroundColor Green
    & agy --dangerously-skip-permissions @ArgsList
}

# Aliases de conveniência
Set-Alias -Name agyw -Value agy-worker -ErrorAction SilentlyContinue
Set-Alias -Name agyl -Value agy-leader -ErrorAction SilentlyContinue
