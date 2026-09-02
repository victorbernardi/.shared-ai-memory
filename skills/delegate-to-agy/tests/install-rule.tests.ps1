$ErrorActionPreference = 'Stop'

$installer = Join-Path $PSScriptRoot '..\scripts\install-rule.ps1'
$configHome = [Environment]::GetEnvironmentVariable('CODEX_HOME', 'Process')
$activeWrapper = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.agents\skills\delegate-to-agy\scripts\invoke-agy.ps1'

if ([string]::IsNullOrWhiteSpace($configHome)) {
    throw 'The regression test requires the managed CODEX_HOME environment variable.'
}
if (-not (Test-Path -LiteralPath $activeWrapper -PathType Leaf)) {
    throw "Expected active wrapper is missing: $activeWrapper"
}

$output = @(& pwsh.exe -NoProfile -File $installer 2>&1)
$exitCode = $LASTEXITCODE
$text = $output -join "`n"
$escapedActiveWrapper = $activeWrapper.Replace('\', '\\').Replace('"', '\"')

if ($exitCode -ne 0) {
    throw "install-rule preview failed with exit $exitCode`n$text"
}
if ($text -notmatch [regex]::Escape($escapedActiveWrapper)) {
    throw "install-rule preview did not target the active wrapper: $activeWrapper`n$text"
}
if ($text -notmatch 'Preview only') {
    throw "install-rule preview did not remain preview-only`n$text"
}

Write-Output 'install-rule root-resolution test passed'
