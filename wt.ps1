param([Parameter(ValueFromRemainingArguments=$true)]$args)

$pythonScript = Join-Path $PSScriptRoot "worktree-manager.py"
if (-not (Test-Path $pythonScript)) {
    Write-Error "Error: Could not find worktree-manager.py"
    exit 1
}

# Run the Python script and capture output
$arguments = @($pythonScript) + $args
if ($arguments.Count -gt 1) {
    $process = Start-Process -FilePath "python" -ArgumentList $arguments -NoNewWindow -Wait -PassThru -RedirectStandardOutput "stdout.tmp" -RedirectStandardError "stderr.tmp"
} else {
    $process = Start-Process -FilePath "python" -ArgumentList @($pythonScript) -NoNewWindow -Wait -PassThru -RedirectStandardOutput "stdout.tmp" -RedirectStandardError "stderr.tmp"
}

# Show stderr output (status messages)
if (Test-Path "stderr.tmp") {
    Get-Content "stderr.tmp" | Write-Host
    Remove-Item "stderr.tmp" -Force
}

# Handle stdout output
$targetDir = $null
if (Test-Path "stdout.tmp") {
    $output = Get-Content "stdout.tmp"
    Remove-Item "stdout.tmp" -Force

    foreach ($line in $output) {
        if (Test-Path $line -PathType Container) {
            $targetDir = $line
        } else {
            Write-Host $line
        }
    }
}

# Change directory if we found a valid directory and not a list command
if ($targetDir -and $process.ExitCode -eq 0 -and $args -notcontains "--list") {
    Set-Location $targetDir
}

exit $process.ExitCode