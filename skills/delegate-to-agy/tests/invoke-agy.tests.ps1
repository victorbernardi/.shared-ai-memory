$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$wrapper = Join-Path $repoRoot 'scripts\invoke-agy.ps1'
$testTempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
$fakeBin = Join-Path $testTempRoot "delegate-to-agy-fake-bin-$([guid]::NewGuid().ToString('N'))"
$originalPath = $env:PATH

New-Item -ItemType Directory -Path $fakeBin | Out-Null
$fakeSource = @'
using System;
using System.Globalization;
using System.IO;
using System.Diagnostics;
using System.Text;
using System.Threading;

public static class Program {
    private static string Json(string value) {
        return (value ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "\\r").Replace("\n", "\\n");
    }

    private static long EnvLong(string name, long fallback) {
        long value;
        return long.TryParse(Environment.GetEnvironmentVariable(name), out value) ? value : fallback;
    }

    private static double EnvDouble(string name, double fallback) {
        double value;
        return double.TryParse(Environment.GetEnvironmentVariable(name), NumberStyles.Float, CultureInfo.InvariantCulture, out value) ? value : fallback;
    }

    public static int Main(string[] args) {
        var argvFile = Environment.GetEnvironmentVariable("FAKE_AGY_ARGV_FILE");
        if (!string.IsNullOrEmpty(argvFile)) {
            var encoded = new string[args.Length];
            for (var i = 0; i < args.Length; i++) encoded[i] = Convert.ToBase64String(Encoding.UTF8.GetBytes(args[i]));
            File.WriteAllLines(argvFile, encoded);
        }
        var status = Environment.GetEnvironmentVariable("FAKE_AGY_STATUS") ?? "SUCCESS";
        var response = Environment.GetEnvironmentVariable("FAKE_AGY_RESPONSE") ?? "";
        var responseLength = EnvLong("FAKE_AGY_RESPONSE_LENGTH", 0);
        if (responseLength > 0) response = new string('x', (int)Math.Min(responseLength, 2000000));
        var error = Environment.GetEnvironmentVariable("FAKE_AGY_ERROR") ?? "";
        var stderr = Environment.GetEnvironmentVariable("FAKE_AGY_STDERR") ?? "";
        var stderrLength = EnvLong("FAKE_AGY_STDERR_LENGTH", 0);
        if (stderrLength > 0) stderr = new string('e', (int)Math.Min(stderrLength, 2000000));
        var conversationId = Environment.GetEnvironmentVariable("FAKE_AGY_CONVERSATION_ID") ?? "00000000-0000-4000-8000-000000000001";
        var startedFile = Environment.GetEnvironmentVariable("FAKE_AGY_STARTED_FILE");
        var childPidFile = Environment.GetEnvironmentVariable("FAKE_AGY_CHILD_PID_FILE");
        var sleepMs = EnvLong("FAKE_AGY_SLEEP_MS", 0);
        var outputPath = Environment.GetEnvironmentVariable("FAKE_AGY_WRITE_OUTPUT");
        var outputContent = Environment.GetEnvironmentVariable("FAKE_AGY_WRITE_CONTENT") ?? "changed";
        if (!string.IsNullOrEmpty(startedFile)) File.WriteAllText(startedFile, "started");
        if (!string.IsNullOrEmpty(childPidFile)) {
            var childStart = new ProcessStartInfo {
                FileName = Environment.GetEnvironmentVariable("ComSpec") ?? "cmd.exe",
                Arguments = "/c ping 127.0.0.1 -n 61 > nul",
                UseShellExecute = false,
                CreateNoWindow = true
            };
            var child = Process.Start(childStart);
            if (child != null) File.WriteAllText(childPidFile, child.Id.ToString(CultureInfo.InvariantCulture));
        }
        if (sleepMs > 0) Thread.Sleep((int)sleepMs);
        if (!string.IsNullOrEmpty(outputPath)) File.WriteAllText(outputPath, outputContent);
        if (!string.IsNullOrEmpty(stderr)) Console.Error.WriteLine(stderr);
        var raw = Environment.GetEnvironmentVariable("FAKE_AGY_RAW");
        if (!string.IsNullOrEmpty(raw)) Console.WriteLine(raw);
        else Console.WriteLine("{\"status\":\"" + Json(status) + "\",\"response\":\"" + Json(response) + "\",\"error\":\"" + Json(error) + "\",\"conversation_id\":\"" + Json(conversationId) + "\",\"duration_seconds\":" + EnvDouble("FAKE_AGY_DURATION", 2).ToString(CultureInfo.InvariantCulture) + ",\"num_turns\":" + EnvLong("FAKE_AGY_TURNS", 1) + ",\"usage\":{\"input_tokens\":" + EnvLong("FAKE_AGY_INPUT", 100) + ",\"output_tokens\":" + EnvLong("FAKE_AGY_OUTPUT", 10) + ",\"thinking_tokens\":" + EnvLong("FAKE_AGY_THINKING", 5) + ",\"cache_read_tokens\":" + EnvLong("FAKE_AGY_CACHE_READ", 50) + ",\"total_tokens\":" + EnvLong("FAKE_AGY_TOTAL", 110) + "}}");
        int code;
        return int.TryParse(Environment.GetEnvironmentVariable("FAKE_AGY_EXIT"), out code) ? code : 0;
    }
}
'@
$fakeSourcePath = Join-Path $fakeBin 'agy.cs'
[System.IO.File]::WriteAllText($fakeSourcePath, $fakeSource)
& 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe' /nologo /target:exe "/out:$(Join-Path $fakeBin 'agy.exe')" $fakeSourcePath
if ($LASTEXITCODE -ne 0) { throw 'Failed to compile fake agy executable.' }

function Assert-Equal {
    param([object]$Actual, [object]$Expected, [string]$Message)
    if ($Actual -ne $Expected) { throw "$Message. Expected '$Expected', got '$Actual'." }
}

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Remove-TestDirectory {
    param([string]$Path, [string]$RequiredNamePrefix)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $tempPrefix = $testTempRoot + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($tempPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        -not [System.IO.Path]::GetFileName($fullPath).StartsWith($RequiredNamePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe test cleanup target: $fullPath"
    }
    $lastError = $null
    for ($cleanupAttempt = 0; $cleanupAttempt -lt 20; $cleanupAttempt++) {
        if (-not (Test-Path -LiteralPath $fullPath)) { return }
        try {
            Remove-Item -LiteralPath $fullPath -Recurse -Force -ErrorAction Stop
            if (-not (Test-Path -LiteralPath $fullPath)) { return }
        } catch {
            $lastError = $_.Exception
        }
        Start-Sleep -Milliseconds 100
    }
    if (Test-Path -LiteralPath $fullPath) {
        throw "Test cleanup failed after bounded retries: $fullPath; $lastError"
    }
}

function Invoke-FakeCase {
    param(
        [string]$Name,
        [string]$Status,
        [string]$ErrorText,
        [int]$FakeExit,
        [string]$RawOutput = '',
        [string]$ResponseText = $null,
        [string]$StderrText = '',
        [bool]$WriteOutput = $true,
        [string]$Kind = 'implement',
        [string]$ConversationId = $null,
        [string]$FakeConversationId = '00000000-0000-4000-8000-000000000001',
        [int]$SleepMs = 0,
        [int]$ResponseLength = 0,
        [int]$StderrLength = 0,
        [switch]$SpawnChild,
        [hashtable]$PreexistingReceipt = $null,
        [string]$InitialOutputContent = $null,
        [switch]$ExpectNoReceipt
    )

    $caseId = [guid]::NewGuid().ToString('N')
    $workspace = Join-Path $testTempRoot "agy-scratch-$caseId"
    $argvFile = Join-Path $testTempRoot "delegate-to-agy-argv-$caseId.json"
    $childPidFile = Join-Path $testTempRoot "delegate-to-agy-child-$caseId.pid"
    New-Item -ItemType Directory -Path (Join-Path $workspace '.agy') | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $workspace 'input.txt'), 'input')
    $taskFile = Join-Path $workspace '.agy\task.json'
    [System.IO.File]::WriteAllText($taskFile, (@{
        schema_version = 1
        workspace_mode = 'scratch'
        kind = $Kind
        objective = "Fake $Name case"
        acceptance_criteria = @('The fake case completes.')
        read_paths = @('input.txt')
        write_paths = @('output.txt')
        out_of_scope = @()
        timeout_seconds = 30
        conversation_id = $ConversationId
    } | ConvertTo-Json))
    if ($null -ne $InitialOutputContent) {
        [System.IO.File]::WriteAllText((Join-Path $workspace 'output.txt'), $InitialOutputContent)
    }
    $receiptPath = Join-Path $workspace '.agy\task.result.json'
    if ($null -ne $PreexistingReceipt) {
        $receiptCopy = [ordered]@{}
        foreach ($entry in $PreexistingReceipt.GetEnumerator()) { $receiptCopy[$entry.Key] = $entry.Value }
        if (-not $PreexistingReceipt.ContainsKey('task_sha256')) {
            $receiptCopy.task_sha256 = (Get-FileHash -LiteralPath $taskFile -Algorithm SHA256).Hash
        }
        if (-not $PreexistingReceipt.ContainsKey('write_state_json')) {
            if (Test-Path -LiteralPath (Join-Path $workspace 'output.txt') -PathType Leaf) {
                $outputHash = (Get-FileHash -LiteralPath (Join-Path $workspace 'output.txt') -Algorithm SHA256).Hash
                $receiptCopy.write_state_json = '{"file:output.txt":"' + $outputHash + '"}'
            } else {
                $receiptCopy.write_state_json = '{"missing:output.txt":"missing"}'
            }
        }
        if (-not $PreexistingReceipt.ContainsKey('write_state_before_json')) {
            $receiptCopy.write_state_before_json = '{"missing:output.txt":"missing"}'
        }
        if (-not $PreexistingReceipt.ContainsKey('model')) {
            $receiptCopy.model = 'gemini-3.7-flash-high'
        }
        if (-not $PreexistingReceipt.ContainsKey('changed_paths')) {
            $receiptCopy.changed_paths = if ($null -ne $PreexistingReceipt['semantic_probe']) { @($PreexistingReceipt['semantic_probe'].changed_paths) } else { @('output.txt') }
        }
        if (-not $PreexistingReceipt.ContainsKey('attempts')) {
            $receiptCopy.attempts = @()
        }
        if (-not $PreexistingReceipt.ContainsKey('completed_at_utc')) {
            $receiptCopy.completed_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
        }
        [System.IO.File]::WriteAllText($receiptPath, ($receiptCopy | ConvertTo-Json -Depth 10))
    }

    try {
        $env:PATH = "$fakeBin;$originalPath"
        $env:FAKE_AGY_STATUS = $Status
        $env:FAKE_AGY_ERROR = $ErrorText
        $env:FAKE_AGY_RESPONSE = if ($PSBoundParameters.ContainsKey('ResponseText')) { $ResponseText } elseif ($Status -eq 'SUCCESS') { 'done' } else { '' }
        $env:FAKE_AGY_STDERR = $StderrText
        $env:FAKE_AGY_STDERR_LENGTH = [string]$StderrLength
        $env:FAKE_AGY_CONVERSATION_ID = $FakeConversationId
        $env:FAKE_AGY_SLEEP_MS = [string]$SleepMs
        $env:FAKE_AGY_RESPONSE_LENGTH = [string]$ResponseLength
        $env:FAKE_AGY_CHILD_PID_FILE = if ($SpawnChild) { $childPidFile } else { '' }
        $env:FAKE_AGY_WRITE_OUTPUT = if ($WriteOutput) { 'output.txt' } else { '' }
        $env:FAKE_AGY_WRITE_CONTENT = "changed-$Name"
        $env:FAKE_AGY_EXIT = [string]$FakeExit
        $env:FAKE_AGY_RAW = $RawOutput
        $env:FAKE_AGY_ARGV_FILE = $argvFile
        $env:FAKE_AGY_INPUT = '100'
        $env:FAKE_AGY_OUTPUT = '10'
        $env:FAKE_AGY_THINKING = '5'
        $env:FAKE_AGY_CACHE_READ = '50'
        $env:FAKE_AGY_TOTAL = '110'
        $env:FAKE_AGY_TURNS = '1'
        $env:FAKE_AGY_DURATION = '2'
        $output = @(& pwsh -NoProfile -File $wrapper -TaskFile $taskFile 2>&1)
        $exitCode = $LASTEXITCODE
        if (-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)) {
            if ($ExpectNoReceipt) {
                return [pscustomobject]@{ ExitCode = $exitCode; Receipt = $null; Argv = @(); Output = $output; ChildPid = $null }
            }
            throw "Wrapper did not create a receipt (exit $exitCode): $($output -join [Environment]::NewLine)"
        }
        $receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
        $argv = if (Test-Path -LiteralPath $argvFile) {
            @(Get-Content -LiteralPath $argvFile | ForEach-Object {
                [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_))
            })
        } else { @() }
        $childPid = $null
        if (Test-Path -LiteralPath $childPidFile) {
            $parsedChildPid = 0
            if ([int]::TryParse((Get-Content -LiteralPath $childPidFile -Raw), [ref]$parsedChildPid)) { $childPid = $parsedChildPid }
        }
        return [pscustomobject]@{ ExitCode = $exitCode; Receipt = $receipt; Argv = @($argv); Output = $output; ChildPid = $childPid }
    } finally {
        $env:PATH = $originalPath
        Remove-Item Env:FAKE_AGY_STATUS, Env:FAKE_AGY_ERROR, Env:FAKE_AGY_RESPONSE, Env:FAKE_AGY_STDERR, Env:FAKE_AGY_STDERR_LENGTH, Env:FAKE_AGY_CONVERSATION_ID, Env:FAKE_AGY_SLEEP_MS, Env:FAKE_AGY_RESPONSE_LENGTH, Env:FAKE_AGY_CHILD_PID_FILE, Env:FAKE_AGY_WRITE_OUTPUT, Env:FAKE_AGY_WRITE_CONTENT, Env:FAKE_AGY_EXIT, Env:FAKE_AGY_RAW, Env:FAKE_AGY_ARGV_FILE, Env:FAKE_AGY_INPUT, Env:FAKE_AGY_OUTPUT, Env:FAKE_AGY_THINKING, Env:FAKE_AGY_CACHE_READ, Env:FAKE_AGY_TOTAL, Env:FAKE_AGY_TURNS, Env:FAKE_AGY_DURATION -ErrorAction SilentlyContinue
        Remove-TestDirectory -Path $workspace -RequiredNamePrefix 'agy-scratch-'
        if (Test-Path -LiteralPath $argvFile) { Remove-Item -LiteralPath $argvFile -Force }
        if (Test-Path -LiteralPath $childPidFile) {
            $cleanupChildPid = 0
            if ([int]::TryParse((Get-Content -LiteralPath $childPidFile -Raw), [ref]$cleanupChildPid)) {
                try { Stop-Process -Id $cleanupChildPid -Force -ErrorAction SilentlyContinue } catch { }
            }
            Remove-Item -LiteralPath $childPidFile -Force -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-FakeConcurrentCase {
    $caseId = [guid]::NewGuid().ToString('N')
    $workspace = Join-Path $testTempRoot "agy-scratch-$caseId"
    $taskDirectory = Join-Path $workspace '.agy'
    $taskFile = Join-Path $taskDirectory 'task.json'
    $stdoutOne = Join-Path $testTempRoot "delegate-to-agy-concurrency-$caseId-1.out"
    $stderrOne = Join-Path $testTempRoot "delegate-to-agy-concurrency-$caseId-1.err"
    $stdoutTwo = Join-Path $testTempRoot "delegate-to-agy-concurrency-$caseId-2.out"
    $stderrTwo = Join-Path $testTempRoot "delegate-to-agy-concurrency-$caseId-2.err"
    $startedFile = Join-Path $testTempRoot "delegate-to-agy-concurrency-$caseId.started"
    New-Item -ItemType Directory -Path $taskDirectory | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $workspace 'input.txt'), 'input')
    [System.IO.File]::WriteAllText($taskFile, (@{
        schema_version = 1
        workspace_mode = 'scratch'
        kind = 'implement'
        objective = 'Serialize concurrent fake invocations.'
        acceptance_criteria = @('The fake case completes.')
        read_paths = @('input.txt')
        write_paths = @('output.txt')
        out_of_scope = @()
        timeout_seconds = 30
        conversation_id = $null
    } | ConvertTo-Json))

    try {
        $env:PATH = "$fakeBin;$originalPath"
        $env:FAKE_AGY_STATUS = 'SUCCESS'
        $env:FAKE_AGY_ERROR = ''
        $env:FAKE_AGY_RESPONSE = 'done'
        $env:FAKE_AGY_STDERR = ''
        $env:FAKE_AGY_CONVERSATION_ID = '00000000-0000-4000-8000-000000000001'
        $env:FAKE_AGY_STARTED_FILE = $startedFile
        $env:FAKE_AGY_SLEEP_MS = '10000'
        $env:FAKE_AGY_WRITE_OUTPUT = 'output.txt'
        $env:FAKE_AGY_WRITE_CONTENT = 'concurrent'
        $env:FAKE_AGY_EXIT = '0'
        $pwshPath = (Get-Command pwsh -CommandType Application | Select-Object -First 1).Source
        $first = Start-Process -FilePath $pwshPath -ArgumentList @('-NoProfile', '-File', $wrapper, '-TaskFile', $taskFile) -WorkingDirectory $workspace -RedirectStandardOutput $stdoutOne -RedirectStandardError $stderrOne -PassThru
        $deadline = [DateTime]::UtcNow.AddSeconds(15)
        while (-not (Test-Path -LiteralPath $startedFile) -and [DateTime]::UtcNow -lt $deadline) {
            Start-Sleep -Milliseconds 50
        }
        if (-not (Test-Path -LiteralPath $startedFile)) {
            $diagnostic = if (Test-Path -LiteralPath $stderrOne) { Get-Content -LiteralPath $stderrOne -Raw } else { '' }
            throw "The first concurrent fixture did not start AGY: $diagnostic"
        }
        $second = Start-Process -FilePath $pwshPath -ArgumentList @('-NoProfile', '-File', $wrapper, '-TaskFile', $taskFile) -WorkingDirectory $workspace -RedirectStandardOutput $stdoutTwo -RedirectStandardError $stderrTwo -PassThru
        $second.WaitForExit()
        $first.WaitForExit()
        $receiptPath = Join-Path $workspace '.agy\task.result.json'
        if (-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)) { throw 'Concurrent fixture did not create a receipt.' }
        return [pscustomobject]@{
            FirstExitCode = $first.ExitCode
            SecondExitCode = $second.ExitCode
            Receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
        }
    } finally {
        $env:PATH = $originalPath
        Remove-Item Env:FAKE_AGY_STATUS, Env:FAKE_AGY_ERROR, Env:FAKE_AGY_RESPONSE, Env:FAKE_AGY_STDERR, Env:FAKE_AGY_CONVERSATION_ID, Env:FAKE_AGY_STARTED_FILE, Env:FAKE_AGY_SLEEP_MS, Env:FAKE_AGY_WRITE_OUTPUT, Env:FAKE_AGY_WRITE_CONTENT, Env:FAKE_AGY_EXIT -ErrorAction SilentlyContinue
        Remove-TestDirectory -Path $workspace -RequiredNamePrefix 'agy-scratch-'
        foreach ($path in @($stdoutOne, $stderrOne, $stdoutTwo, $stderrTwo, $startedFile)) {
            if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
        }
    }
}

function Invoke-FakeUsageSequence {
    $caseId = [guid]::NewGuid().ToString('N')
    $workspace = Join-Path $testTempRoot "agy-scratch-$caseId"
    $taskDirectory = Join-Path $workspace '.agy'
    $taskFile = Join-Path $taskDirectory 'task.json'
    $receiptFile = Join-Path $taskDirectory 'task.result.json'
    New-Item -ItemType Directory -Path $taskDirectory | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $workspace 'input.txt'), 'input')
    $task = [ordered]@{
        schema_version = 1
        workspace_mode = 'scratch'
        kind = 'implement'
        objective = 'Record implementation usage.'
        acceptance_criteria = @('Usage is recorded.')
        read_paths = @('input.txt')
        write_paths = @('output.txt')
        out_of_scope = @()
        timeout_seconds = 30
        conversation_id = $null
    }

    try {
        $env:PATH = "$fakeBin;$originalPath"
        $env:FAKE_AGY_STATUS = 'SUCCESS'
        $env:FAKE_AGY_RESPONSE = 'done'
        $env:FAKE_AGY_ERROR = ''
        $env:FAKE_AGY_STDERR = ''
        $env:FAKE_AGY_WRITE_OUTPUT = 'output.txt'
        $env:FAKE_AGY_WRITE_CONTENT = 'initial'
        $env:FAKE_AGY_EXIT = '0'
        $env:FAKE_AGY_INPUT = '100'
        $env:FAKE_AGY_OUTPUT = '10'
        $env:FAKE_AGY_THINKING = '5'
        $env:FAKE_AGY_CACHE_READ = '50'
        $env:FAKE_AGY_TOTAL = '110'
        $env:FAKE_AGY_TURNS = '1'
        $env:FAKE_AGY_DURATION = '2'
        [System.IO.File]::WriteAllText($taskFile, ($task | ConvertTo-Json))
        & pwsh -NoProfile -File $wrapper -TaskFile $taskFile | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'Initial usage fixture failed.' }

        $task.kind = 'remediate'
        $task.objective = 'Record remediation usage.'
        $task.conversation_id = '00000000-0000-4000-8000-000000000001'
        [System.IO.File]::WriteAllText($taskFile, ($task | ConvertTo-Json))
        $env:FAKE_AGY_INPUT = '160'
        $env:FAKE_AGY_OUTPUT = '20'
        $env:FAKE_AGY_THINKING = '8'
        $env:FAKE_AGY_CACHE_READ = '80'
        $env:FAKE_AGY_TOTAL = '180'
        $env:FAKE_AGY_TURNS = '2'
        $env:FAKE_AGY_DURATION = '3.5'
        $env:FAKE_AGY_WRITE_CONTENT = 'remediated'
        & pwsh -NoProfile -File $wrapper -TaskFile $taskFile | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'Remediation usage fixture failed.' }

        $task.objective = 'Record failed remediation usage.'
        [System.IO.File]::WriteAllText($taskFile, ($task | ConvertTo-Json))
        $env:FAKE_AGY_STATUS = 'ERROR'
        $env:FAKE_AGY_RESPONSE = ''
        $env:FAKE_AGY_ERROR = 'permission denied by sandbox'
        $env:FAKE_AGY_STDERR = 'permission denied by sandbox'
        $env:FAKE_AGY_WRITE_OUTPUT = ''
        $env:FAKE_AGY_EXIT = '1'
        $env:FAKE_AGY_INPUT = '170'
        $env:FAKE_AGY_OUTPUT = '22'
        $env:FAKE_AGY_THINKING = '9'
        $env:FAKE_AGY_CACHE_READ = '85'
        $env:FAKE_AGY_TOTAL = '192'
        $env:FAKE_AGY_TURNS = '3'
        $env:FAKE_AGY_DURATION = '4'
        & pwsh -NoProfile -File $wrapper -TaskFile $taskFile 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 4) { throw 'Failed remediation usage fixture returned an unexpected exit code.' }

        return Get-Content -LiteralPath $receiptFile -Raw | ConvertFrom-Json
    } finally {
        $env:PATH = $originalPath
        Remove-Item Env:FAKE_AGY_STATUS, Env:FAKE_AGY_RESPONSE, Env:FAKE_AGY_ERROR, Env:FAKE_AGY_STDERR, Env:FAKE_AGY_WRITE_OUTPUT, Env:FAKE_AGY_WRITE_CONTENT, Env:FAKE_AGY_EXIT, Env:FAKE_AGY_INPUT, Env:FAKE_AGY_OUTPUT, Env:FAKE_AGY_THINKING, Env:FAKE_AGY_CACHE_READ, Env:FAKE_AGY_TOTAL, Env:FAKE_AGY_TURNS, Env:FAKE_AGY_DURATION -ErrorAction SilentlyContinue
        Remove-TestDirectory -Path $workspace -RequiredNamePrefix 'agy-scratch-'
    }
}

try {
    $permission = Invoke-FakeCase -Name 'permission' -Status 'ERROR' -ErrorText 'git grep denied by sandbox permission' -FakeExit 1
    Assert-Equal $permission.ExitCode 4 'Permission denial wrapper exit code'
    Assert-Equal $permission.Receipt.category 'permission_denied' 'Permission denial category'
    Assert-Equal $permission.Receipt.retryable $false 'Permission denial retryability'
    Assert-Equal $permission.Receipt.attempts.Count 1 'Permission denial attempt count'
    Assert-Equal $permission.Receipt.attempts[0].usage_delta.total_tokens 110 'Permission denial loop token usage'
    Assert-True ($permission.Receipt.PSObject.Properties.Name -notcontains 'conversation_id') 'Failure receipts must omit raw conversation IDs.'
    Assert-True ($permission.Receipt.PSObject.Properties.Name -notcontains 'error') 'Failure receipts must omit raw AGY error text.'

    $unavailable = Invoke-FakeCase -Name 'unavailable' -Status 'ERROR' -ErrorText 'Sandbox backend is UNAVAILABLE (code 503)' -FakeExit 1
    Assert-Equal $unavailable.Receipt.category 'transient_unavailable' 'Unavailable category'
    Assert-Equal $unavailable.Receipt.retryable $true 'Unavailable retryability'

    $canceled = Invoke-FakeCase -Name 'canceled' -Status 'CANCELED' -ErrorText '' -FakeExit 1
    Assert-Equal $canceled.Receipt.category 'canceled' 'Canceled category'
    Assert-Equal $canceled.Receipt.retryable $false 'Canceled retryability'

    $timeout = Invoke-FakeCase -Name 'timeout' -Status 'TIMEOUT' -ErrorText 'sandbox operation timed out' -FakeExit 1
    Assert-Equal $timeout.Receipt.category 'timeout' 'Timeout category'
    Assert-Equal $timeout.Receipt.retryable $false 'Timeout retryability'

    $processTimeout = Invoke-FakeCase -Name 'process-timeout' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -SleepMs 31000 -SpawnChild
    Assert-Equal $processTimeout.ExitCode 4 'Hung process wrapper exit code'
    Assert-Equal $processTimeout.Receipt.category 'timeout' 'Hung process category'
    Assert-Equal $processTimeout.Receipt.status 'NEEDS_FOLLOWUP' 'Hung process receipt status'
    Assert-True ($null -ne $processTimeout.ChildPid) 'Hung process fixture must record child PID'
    Start-Sleep -Milliseconds 250
    Assert-True ($null -eq (Get-Process -Id $processTimeout.ChildPid -ErrorAction SilentlyContinue)) 'Hung process child must be terminated with parent tree'

    $emptyResponse = Invoke-FakeCase -Name 'empty-response' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -ResponseText '   '
    Assert-Equal $emptyResponse.ExitCode 4 'Empty response wrapper exit code'
    Assert-Equal $emptyResponse.Receipt.status 'NEEDS_FOLLOWUP' 'Empty response receipt status'
    Assert-Equal $emptyResponse.Receipt.category 'empty_response' 'Empty response category'
    Assert-Equal $emptyResponse.Receipt.agy_status 'SUCCESS' 'Empty response terminal status'
    Assert-Equal $emptyResponse.Receipt.response_summary.present $false 'Empty response summary'
    Assert-True (($emptyResponse.Receipt | ConvertTo-Json -Depth 10) -notmatch 'done') 'Empty response receipt must not invent response text'
    Assert-True (($emptyResponse.Output -join [Environment]::NewLine) -match '"status":"NEEDS_FOLLOWUP"') 'Failure wrapper output status'

    $genericTerminalError = Invoke-FakeCase -Name 'generic-terminal-error' -Status 'SUCCESS' -ErrorText 'read_file failed: unexpected terminal response' -FakeExit 0 -ResponseText 'done'
    Assert-Equal $genericTerminalError.ExitCode 4 'Generic terminal error wrapper exit code'
    Assert-Equal $genericTerminalError.Receipt.status 'NEEDS_FOLLOWUP' 'Generic terminal error receipt status'
    Assert-Equal $genericTerminalError.Receipt.category 'terminal_error' 'Generic terminal error category'
    Assert-True (($genericTerminalError.Output -join [Environment]::NewLine) -match '"status":"NEEDS_FOLLOWUP"') 'Generic terminal error wrapper output status'

    $poisonedCache = Invoke-FakeCase -Name 'poisoned-cache' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -PreexistingReceipt @{
        schema_version = 1
        status = 'SUCCESS'
        classification = 'permission_denied'
        terminal_status = 'ERROR'
        agy_status = 'ERROR'
        agy_exit_code = 1
        response_summary = @{ present = $true; length = 4; line_count = 1 }
        stderr_summary = @{ present = $false; length = 0; line_count = 0; signals = @() }
        semantic_probe = @{ required = $true; kind = 'allowed_write_change'; passed = $true; changed_paths = @('output.txt') }
        conversation_id = '00000000-0000-4000-8000-000000000001'
    }
    Assert-Equal $poisonedCache.ExitCode 0 'Poisoned cache must be re-executed'
    Assert-True ($poisonedCache.Argv.Count -gt 0) 'Poisoned cache must not bypass AGY'
    Assert-Equal $poisonedCache.Receipt.status 'SUCCESS' 'Re-executed cache receipt status'
    Assert-Equal $poisonedCache.Receipt.classification 'success' 'Re-executed cache classification'

    $malformedCacheState = Invoke-FakeCase -Name 'malformed-cache-state' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -InitialOutputContent 'existing' -PreexistingReceipt @{
        schema_version = 1
        status = 'SUCCESS'
        classification = 'success'
        terminal_status = 'SUCCESS'
        agy_status = 'SUCCESS'
        agy_exit_code = 0
        write_state_before_json = '{}'
        response_summary = @{ present = $true; length = 4; line_count = 1 }
        stderr_summary = @{ present = $false; length = 0; line_count = 0; signals = @() }
        semantic_probe = @{ required = $true; kind = 'allowed_write_change'; passed = $true; changed_paths = @('output.txt') }
        changed_paths = @('output.txt')
        conversation_id = '00000000-0000-4000-8000-000000000001'
    }
    Assert-True ($malformedCacheState.Argv.Count -gt 0) 'Malformed cache write state must not bypass AGY'
    Assert-Equal $malformedCacheState.Receipt.classification 'success' 'Malformed cache must be replaced by a fresh success'

    $unrelatedCachePath = Invoke-FakeCase -Name 'unrelated-cache-path' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -InitialOutputContent 'existing' -PreexistingReceipt @{
        schema_version = 1
        status = 'SUCCESS'
        classification = 'success'
        terminal_status = 'SUCCESS'
        agy_status = 'SUCCESS'
        agy_exit_code = 0
        write_state_before_json = '{"missing:output.txt":"missing"}'
        response_summary = @{ present = $true; length = 4; line_count = 1 }
        stderr_summary = @{ present = $false; length = 0; line_count = 0; signals = @() }
        semantic_probe = @{ required = $true; kind = 'allowed_write_change'; passed = $true; changed_paths = @('secret.txt') }
        changed_paths = @('secret.txt')
        conversation_id = '00000000-0000-4000-8000-000000000001'
    }
    Assert-True ($unrelatedCachePath.Argv.Count -gt 0) 'Cache changed paths outside the allowlist must not bypass AGY'
    Assert-Equal $unrelatedCachePath.Receipt.classification 'success' 'Unrelated cache path must be replaced by a fresh success'

    $untrustedAttempts = Invoke-FakeCase -Name 'untrusted-attempts' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -InitialOutputContent 'existing' -PreexistingReceipt @{
        schema_version = 1
        status = 'SUCCESS'
        classification = 'success'
        terminal_status = 'SUCCESS'
        agy_status = 'SUCCESS'
        agy_exit_code = 0
        write_state_before_json = '{"missing:output.txt":"missing"}'
        response_summary = @{ present = $true; length = 4; line_count = 1 }
        stderr_summary = @{ present = $false; length = 0; line_count = 0; signals = @() }
        semantic_probe = @{ required = $true; kind = 'allowed_write_change'; passed = $true; changed_paths = @('output.txt') }
        changed_paths = @('output.txt')
        conversation_id = '00000000-0000-4000-8000-000000000001'
        attempts = @(@{ response = 'attempt-secret'; sequence = 1 })
    }
    Assert-True ($untrustedAttempts.Argv.Count -gt 0) 'Untrusted attempts must invalidate the cache'
    Assert-True (($untrustedAttempts.Receipt | ConvertTo-Json -Depth 12) -notmatch 'attempt-secret') 'Untrusted attempt fields must not persist'
    Assert-Equal $untrustedAttempts.Receipt.attempts.Count 1 'Invalid prior attempts must be discarded'

    $emptyRemediation = Invoke-FakeCase -Name 'empty-remediation-conversation' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -Kind 'remediate' -ConversationId '00000000-0000-0000-0000-000000000000' -ExpectNoReceipt
    Assert-Equal $emptyRemediation.ExitCode 2 'Empty remediation conversation must fail preflight'
    Assert-True ($null -eq $emptyRemediation.Receipt) 'Empty remediation conversation must not create a receipt'

    $mismatchedRemediation = Invoke-FakeCase -Name 'mismatched-remediation-conversation' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -Kind 'remediate' -ConversationId '00000000-0000-4000-8000-000000000001' -FakeConversationId '00000000-0000-4000-8000-000000000002'
    Assert-Equal $mismatchedRemediation.ExitCode 4 'Mismatched remediation conversation exit code'
    Assert-Equal $mismatchedRemediation.Receipt.category 'conversation_mismatch' 'Mismatched remediation conversation category'
    Assert-Equal $mismatchedRemediation.Receipt.status 'NEEDS_FOLLOWUP' 'Mismatched remediation conversation status'

    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $initialOutputHash = [Convert]::ToHexString($sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes('initial')))
    } finally {
        $sha256.Dispose()
    }
    $remediationNoCache = Invoke-FakeCase -Name 'remediation-no-cache' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -Kind 'remediate' -ConversationId '00000000-0000-4000-8000-000000000001' -InitialOutputContent 'initial' -PreexistingReceipt @{
        schema_version = 1
        status = 'SUCCESS'
        classification = 'success'
        terminal_status = 'SUCCESS'
        agy_status = 'SUCCESS'
        agy_exit_code = 0
        write_state_json = '{"file:output.txt":"' + $initialOutputHash + '"}'
        write_state_before_json = '{"missing:output.txt":"missing"}'
        response_summary = @{ present = $true; length = 4; line_count = 1 }
        stderr_summary = @{ present = $false; length = 0; line_count = 0; signals = @() }
        semantic_probe = @{ required = $true; kind = 'allowed_write_change'; passed = $true; changed_paths = @('output.txt') }
        conversation_id = '00000000-0000-4000-8000-000000000001'
    }
    Assert-Equal $remediationNoCache.ExitCode 0 'Remediation must execute despite matching receipt task hash'
    Assert-True ($remediationNoCache.Argv.Count -gt 0) 'Remediation must not be served from cache'
    Assert-Equal $remediationNoCache.Receipt.attempts.Count 1 'Remediation execution attempt count'

    $stderrDenial = Invoke-FakeCase -Name 'stderr-denial' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -StderrText 'read_file denied by sandbox for secret-token=should-not-persist'
    Assert-Equal $stderrDenial.ExitCode 4 'stderr denial wrapper exit code'
    Assert-Equal $stderrDenial.Receipt.status 'NEEDS_FOLLOWUP' 'stderr denial receipt status'
    Assert-Equal $stderrDenial.Receipt.category 'permission_denied' 'stderr denial category'
    Assert-True ($stderrDenial.Receipt.stderr_summary.signals -contains 'permission_denied') 'stderr denial signal'
    Assert-True (($stderrDenial.Receipt | ConvertTo-Json -Depth 10) -notmatch 'should-not-persist|read_file denied') 'stderr receipt must not persist raw denial'
    Assert-True (($stderrDenial.Output -join [Environment]::NewLine) -notmatch 'should-not-persist|read_file denied') 'stderr denial must not leak through wrapper output'

    $hardStderr = Invoke-FakeCase -Name 'stderr-overrides-transient' -Status 'ERROR' -ErrorText 'backend temporarily UNAVAILABLE' -FakeExit 1 -StderrText 'read_file permission denied'
    Assert-Equal $hardStderr.Receipt.category 'permission_denied' 'Hard stderr signal must override transient terminal evidence'

    $eacces = Invoke-FakeCase -Name 'eacces' -Status 'ERROR' -ErrorText 'read_file failed: EACCES' -FakeExit 1
    Assert-Equal $eacces.Receipt.category 'permission_denied' 'EACCES must be classified as permission denial'

    $eperm = Invoke-FakeCase -Name 'eperm' -Status 'ERROR' -ErrorText 'operation failed with EPERM' -FakeExit 1
    Assert-Equal $eperm.Receipt.category 'permission_denied' 'EPERM must be classified as permission denial'

    $rawEacces = Invoke-FakeCase -Name 'raw-eacces' -Status 'ERROR' -ErrorText '' -FakeExit 1 -RawOutput 'not-json' -StderrText 'EACCES: read denied'
    Assert-Equal $rawEacces.Receipt.category 'permission_denied' 'Raw EACCES must be classified as permission denial'

    $rawTransient = Invoke-FakeCase -Name 'raw-transient' -Status 'ERROR' -ErrorText '' -FakeExit 1 -RawOutput 'not-json' -StderrText 'temporary error while contacting backend'
    Assert-Equal $rawTransient.Receipt.category 'transient_unavailable' 'Raw temporary error must be retryable transient'

    $stderrTransient = Invoke-FakeCase -Name 'stderr-transient' -Status 'ERROR' -ErrorText '' -FakeExit 1 -StderrText 'backend temporary error'
    Assert-Equal $stderrTransient.Receipt.category 'transient_unavailable' 'Transient stderr must override generic stderr error'

    $benignStderr = Invoke-FakeCase -Name 'benign-stderr' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -StderrText 'sandbox mode enabled'
    Assert-Equal $benignStderr.ExitCode 0 'Benign stderr wrapper exit code'
    Assert-Equal $benignStderr.Receipt.status 'SUCCESS' 'Benign stderr receipt status'
    Assert-Equal $benignStderr.Receipt.stderr_summary.signals.Count 0 'Benign stderr signals'

    $benignDiagnostics = Invoke-FakeCase -Name 'benign-diagnostics' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -StderrText 'permission model initialized; temporary workspace selected'
    Assert-Equal $benignDiagnostics.ExitCode 0 'Benign permission and temporary diagnostics exit code'
    Assert-Equal $benignDiagnostics.Receipt.stderr_summary.signals.Count 0 'Benign permission and temporary diagnostics must not be hard failures'

    $outputOverflow = Invoke-FakeCase -Name 'output-overflow' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -ResponseLength 1100000
    Assert-Equal $outputOverflow.ExitCode 4 'Oversized AGY output wrapper exit code'
    Assert-Equal $outputOverflow.Receipt.category 'invalid_terminal_output' 'Oversized AGY output category'
    Assert-Equal $outputOverflow.Receipt.status 'NEEDS_FOLLOWUP' 'Oversized AGY output receipt status'
    Assert-True (($outputOverflow.Receipt | ConvertTo-Json -Depth 12).Length -lt 100000) 'Oversized AGY output must not persist raw output'

    $stderrOverflow = Invoke-FakeCase -Name 'stderr-overflow' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -StderrLength 1100000
    Assert-Equal $stderrOverflow.ExitCode 4 'Oversized AGY stderr wrapper exit code'
    Assert-Equal $stderrOverflow.Receipt.category 'invalid_terminal_output' 'Oversized AGY stderr category'
    Assert-True (($stderrOverflow.Receipt | ConvertTo-Json -Depth 12).Length -lt 100000) 'Oversized AGY stderr must not persist raw output'

    $sensitiveResponse = Invoke-FakeCase -Name 'sensitive-response' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -ResponseText 'access_token=should-not-persist'
    Assert-Equal $sensitiveResponse.ExitCode 0 'Sensitive response wrapper exit code'
    Assert-True (($sensitiveResponse.Output -join [Environment]::NewLine) -notmatch 'should-not-persist') 'Raw response must not leak through wrapper output'
    Assert-True (($sensitiveResponse.Receipt | ConvertTo-Json -Depth 10) -notmatch 'should-not-persist') 'Raw response must not persist in receipt'

    $noMutation = Invoke-FakeCase -Name 'no-mutation' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -WriteOutput $false
    Assert-Equal $noMutation.ExitCode 4 'No mutation wrapper exit code'
    Assert-Equal $noMutation.Receipt.status 'NEEDS_FOLLOWUP' 'No mutation receipt status'
    Assert-Equal $noMutation.Receipt.category 'no_mutation_evidence' 'No mutation category'
    Assert-Equal $noMutation.Receipt.semantic_probe.passed $false 'No mutation probe result'
    Assert-Equal $noMutation.Receipt.semantic_probe.changed_paths.Count 0 'No mutation changed paths'

    $concurrent = Invoke-FakeConcurrentCase
    Assert-Equal $concurrent.FirstExitCode 0 'First concurrent invocation exit code'
    Assert-Equal $concurrent.SecondExitCode 3 'Second concurrent invocation must be rejected'
    Assert-Equal $concurrent.Receipt.status 'SUCCESS' 'Concurrent receipt must come from the first invocation'

    $invalid = Invoke-FakeCase -Name 'invalid' -Status 'ERROR' -ErrorText '' -FakeExit 1 -RawOutput 'not-json'
    Assert-Equal $invalid.Receipt.category 'invalid_terminal_output' 'Invalid output category'
    Assert-Equal $invalid.Receipt.retryable $false 'Invalid output retryability'

    $unknownStatus = Invoke-FakeCase -Name 'unknown-status' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -RawOutput '{"status":"UNKNOWN_SECRET_STATUS","response":"done","error":"","conversation_id":"00000000-0000-4000-8000-000000000001"}'
    Assert-Equal $unknownStatus.Receipt.category 'invalid_terminal_output' 'Unknown status category'
    Assert-True ($null -eq $unknownStatus.Receipt.terminal_status) 'Unknown status must not be persisted'
    Assert-True (($unknownStatus.Receipt | ConvertTo-Json -Depth 10) -notmatch 'UNKNOWN_SECRET_STATUS') 'Unknown status must not leak into receipt'

    $malformedResponse = Invoke-FakeCase -Name 'malformed-response' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -RawOutput '{"status":"SUCCESS","response":{"secret":"should-not-persist"},"error":"","conversation_id":"00000000-0000-4000-8000-000000000001"}'
    Assert-Equal $malformedResponse.Receipt.category 'invalid_terminal_output' 'Malformed response category'
    Assert-True (($malformedResponse.Receipt | ConvertTo-Json -Depth 10) -notmatch 'should-not-persist') 'Malformed response must not leak into receipt'

    $invalidUsage = Invoke-FakeCase -Name 'invalid-usage' -Status 'SUCCESS' -ErrorText '' -FakeExit 0 -RawOutput '{"status":"SUCCESS","response":"done","error":"","conversation_id":"00000000-0000-4000-8000-000000000001","usage":{"input_tokens":"usage-secret","output_tokens":10,"thinking_tokens":5,"cache_read_tokens":50,"total_tokens":110},"num_turns":"turn-secret","duration_seconds":"duration-secret"}'
    Assert-Equal $invalidUsage.ExitCode 0 'Invalid usage metadata must not invalidate an otherwise valid terminal result'
    Assert-True (($invalidUsage.Receipt | ConvertTo-Json -Depth 12) -notmatch 'usage-secret|turn-secret|duration-secret') 'Invalid usage metadata must not persist'
    Assert-True ($null -eq $invalidUsage.Receipt.attempts[0].usage_cumulative) 'Invalid usage metadata must be discarded'

    $success = Invoke-FakeCase -Name 'success' -Status 'SUCCESS' -ErrorText '' -FakeExit 0
    Assert-Equal $success.ExitCode 0 'Success wrapper exit code'
    Assert-Equal $success.Receipt.status 'SUCCESS' 'Success receipt status'
    Assert-Equal $success.Receipt.classification 'success' 'Success classification'
    Assert-Equal $success.Receipt.terminal_status 'SUCCESS' 'Success terminal status'
    Assert-Equal $success.Receipt.agy_exit_code 0 'Success exit code evidence'
    Assert-True ([string]$success.Receipt.task_sha256 -match '^[0-9A-Fa-f]{64}$') 'Success task binding'
    Assert-True (-not [string]::IsNullOrWhiteSpace([string]$success.Receipt.write_state_json)) 'Success write-state binding'
    Assert-Equal $success.Receipt.conversation_id '00000000-0000-4000-8000-000000000001' 'Success conversation binding'
    $safeSuccessOutput = ($success.Output -join [Environment]::NewLine) | ConvertFrom-Json
    Assert-Equal $safeSuccessOutput.status 'SUCCESS' 'Safe output status compatibility'
    Assert-Equal $success.Receipt.response_summary.present $true 'Success response summary'
    Assert-Equal $success.Receipt.stderr_summary.present $false 'Success stderr summary'
    Assert-Equal $success.Receipt.semantic_probe.required $true 'Success semantic probe requirement'
    Assert-Equal $success.Receipt.semantic_probe.passed $true 'Success semantic probe result'
    Assert-True ($success.Receipt.semantic_probe.changed_paths -contains 'output.txt') 'Success semantic probe changed path'
    Assert-Equal $success.Receipt.attempts.Count 1 'Success attempt count'
    Assert-Equal $success.Receipt.attempts[0].category 'success' 'Success attempt classification'
    Assert-Equal $success.Receipt.attempts[0].response_summary.present $true 'Success attempt response summary'
    Assert-Equal $success.Receipt.attempts[0].semantic_probe.passed $true 'Success attempt semantic probe'
    Assert-Equal $success.Receipt.attempts[0].usage_cumulative.input_tokens 100 'Success cumulative input tokens'
    Assert-Equal $success.Receipt.attempts[0].usage_delta.input_tokens 100 'Fresh success loop input tokens'
    Assert-Equal $success.Receipt.attempts[0].num_turns_delta 1 'Fresh success turn delta'
    Assert-True ($success.Argv -contains '--sandbox') 'The wrapper must retain AGY sandbox mode.'
    $modelIndex = [Array]::IndexOf($success.Argv, '--model')
    Assert-True (
        $modelIndex -ge 0 -and
        ($modelIndex + 1) -lt $success.Argv.Count -and
        $success.Argv[$modelIndex + 1] -eq 'gemini-3.7-flash-high'
    ) 'The wrapper must pin the requested AGY model.'
    Assert-True ($success.Argv -notcontains '--dangerously-skip-permissions') 'The wrapper must not skip AGY permissions.'
    $promptIndex = [Array]::IndexOf($success.Argv, '-p') + 1
    Assert-True ($promptIndex -gt 0 -and $success.Argv[$promptIndex] -match 'Do not invoke shell, Git') 'The prompt must prohibit shell and Git commands.'

    $usageSequence = Invoke-FakeUsageSequence
    Assert-Equal $usageSequence.status 'SUCCESS' 'Failed remediation must preserve successful output binding'
    Assert-Equal $usageSequence.attempts.Count 3 'Usage sequence attempt count'
    Assert-Equal $usageSequence.attempts[1].usage_cumulative.total_tokens 180 'Remediation cumulative total tokens'
    Assert-Equal $usageSequence.attempts[1].usage_delta.input_tokens 60 'Remediation input token delta'
    Assert-Equal $usageSequence.attempts[1].usage_delta.total_tokens 70 'Remediation total token delta'
    Assert-Equal $usageSequence.attempts[1].num_turns_delta 1 'Remediation turn delta'
    Assert-Equal $usageSequence.attempts[1].duration_seconds_delta 1.5 'Remediation duration delta'
    Assert-Equal $usageSequence.attempts[2].agy_status 'ERROR' 'Failed remediation terminal status'
    Assert-Equal $usageSequence.attempts[2].category 'permission_denied' 'Failed remediation category'
    Assert-Equal $usageSequence.attempts[2].usage_delta.total_tokens 12 'Failed remediation total token delta'
    Assert-Equal $usageSequence.current_attempt_status 'NEEDS_FOLLOWUP' 'Failed remediation current status'
    Assert-Equal $usageSequence.last_attempt_category 'permission_denied' 'Failed remediation last-attempt category'

    Write-Output 'invoke-agy wrapper tests passed'
} finally {
    Remove-TestDirectory -Path $fakeBin -RequiredNamePrefix 'delegate-to-agy-fake-bin-'
}
