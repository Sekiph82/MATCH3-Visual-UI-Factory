# Offline-first, no GitHub Actions billing and no production asset writes.
# Execute from the existing checkout; no cloning, cleanup or pip installs.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) { throw 'Python 3.11+ is required locally.' }

$version = & $python.Source -c 'import sys; print(sys.version_info.major, sys.version_info.minor)'
if ($LASTEXITCODE -ne 0 -or $version -notmatch '^3\s+(1[1-9]|[2-9]\d)$') {
    throw "Unsupported Python: $version. Install Python 3.11 or newer."
}

$oldBytecode = $env:PYTHONDONTWRITEBYTECODE
$env:PYTHONDONTWRITEBYTECODE = '1'
Push-Location -LiteralPath $project
try {
    $steps = @(
        @{ Label = 'Unit tests'; Args = @('-B','-m','unittest','discover','-s','tests','-v') },
        @{ Label = 'Visual director contracts'; Args = @('-B','factory/validators/validate_design.py') },
        @{ Label = 'Unity source/package structure'; Args = @('-B','Tools/validate_repo_structure.py') },
        @{ Label = 'TEST_ONLY sample manifest'; Args = @('-B','Tools/validate_manifest.py','Samples~/sample_manifest.json') }
    )
    foreach ($step in $steps) {
        Write-Host "RUNNING: $($step.Label)"
        & $python.Source @($step.Args)
        if ($LASTEXITCODE -ne 0) {
            throw "SOURCE_CHECK_FAILED: $($step.Label) (exit $LASTEXITCODE)"
        }
    }
    Write-Host 'All local structural checks PASSED. No Unity Editor / real device signoff implied.'
}
finally {
    Pop-Location
    $env:PYTHONDONTWRITEBYTECODE = $oldBytecode
}
