param(
    [string]$Destination,
    [string]$CodexHome
)

$ErrorActionPreference = 'Stop'
$python = $null
$pythonArgs = @()

$command = Get-Command python -ErrorAction SilentlyContinue
if ($command) {
    $python = $command.Source
} else {
    $command = Get-Command py -ErrorAction SilentlyContinue
    if ($command) {
        $python = $command.Source
        $pythonArgs = @('-3')
    } else {
        $bundled = Join-Path $HOME '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        if (Test-Path -LiteralPath $bundled) { $python = $bundled }
    }
}

if (-not $python) {
    throw 'Python 3 was not found. Run this installer inside Codex or install Python 3, then retry.'
}

$arguments = @($pythonArgs) + @((Join-Path $PSScriptRoot 'install.py'))
if ($Destination) { $arguments += @('--destination', $Destination) }
if ($CodexHome) { $arguments += @('--codex-home', $CodexHome) }
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw "PDOS installer failed with exit code $LASTEXITCODE" }
