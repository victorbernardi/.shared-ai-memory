
Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'chromedriver.exe'" | Where-Object { 
    $_.CommandLine -match "notebooklm" -or 
    $_.CommandLine -match "undetected" -or 
    $_.CommandLine -match "chromedriver" 
} | ForEach-Object { 
    Write-Host "Terminating process: $($_.ProcessId) - $($_.Name)"
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue 
}

$cachePath = "$env:APPDATA\undetected_chromedriver"
if (Test-Path $cachePath) {
    Write-Host "Removing cache: $cachePath"
    Remove-Item -Recurse -Force $cachePath -ErrorAction SilentlyContinue
}
