# Unity 6000.6.5f1 local EditMode source tests, no GitHub Actions, no deletes.
# Nothing executes until the owner runs this script on the existing project.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EvidenceDirectory,
    [string]$UnityExe = ''
)

$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$evidence = [IO.Path]::GetFullPath($EvidenceDirectory)

if ($evidence -eq $project -or
    $evidence.StartsWith($project + [IO.Path]::DirectorySeparatorChar,
                         [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Evidence directory must be OUTSIDE the project checkout.'
}
if (-not (Test-Path -LiteralPath (Join-Path $project 'Packages/manifest.json'))) {
    throw 'This is not the existing MATCH3 Visual Factory project.'
}
$version = Get-Content -LiteralPath (Join-Path $project 'ProjectSettings/ProjectVersion.txt') -Raw
if ($version -notmatch 'm_EditorVersion:\s*6000\.6\.5f1') {
    throw 'Unity project version mismatch. Do not silently upgrade it.'
}
if ([string]::IsNullOrWhiteSpace($UnityExe)) {
    $UnityExe = Join-Path $env:ProgramFiles 'Unity/Hub/Editor/6000.6.5f1/Editor/Unity.exe'
}
if (-not (Test-Path -LiteralPath $UnityExe)) {
    throw "Required Unity Editor not installed: $UnityExe"
}

$git = Get-Command git -ErrorAction SilentlyContinue
if ($null -eq $git) { throw 'Git is required to pin the exact source SHA.' }
Push-Location -LiteralPath $project
try {
    $dirty = @(& $git.Source status --porcelain=v1 --untracked-files=normal)
    if ($LASTEXITCODE -ne 0 -or $dirty.Count -gt 0) {
        throw 'Local checkout is not clean; preserve/inspect changes before running.'
    }
    $sha = (& $git.Source rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $sha.Length -ne 40) {
        throw 'Cannot identify source revision.'
    }
    if (Test-Path -LiteralPath $evidence -PathType Leaf) {
        throw 'Evidence destination is a file.'
    }
    New-Item -ItemType Directory -Force -Path $evidence | Out-Null
    $xmlPath = Join-Path $evidence ("VUF_EditMode_" + $sha.Substring(0,12) + ".xml")
    $logPath = Join-Path $evidence ("VUF_Editor_" + $sha.Substring(0,12) + ".log")
    if ((Test-Path -LiteralPath $xmlPath) -or (Test-Path -LiteralPath $logPath)) {
        throw 'Existing test output is protected; use a different evidence folder.'
    }
    Write-Host "Testing exact source revision $sha, no GitHub Actions."
    $arguments = @(
        '-batchmode', '-nographics', '-quit',
        '-projectPath', ('"' + $project + '"'),
        '-runTests', '-testPlatform', 'EditMode',
        '-testResults', ('"' + $xmlPath + '"'),
        '-logFile', ('"' + $logPath + '"')
    )
    $process = Start-Process -FilePath $UnityExe -ArgumentList $arguments -PassThru -Wait
    if ($process.ExitCode -ne 0) {
        throw "Unity exited $($process.ExitCode). Inspect preserved local log: $logPath"
    }
    if (-not (Test-Path -LiteralPath $xmlPath)) {
        throw "Unity produced no EditMode XML results; cannot claim PASS. Log: $logPath"
    }
    [xml]$result = Get-Content -LiteralPath $xmlPath -Raw
    $testRun = $result.SelectSingleNode('/test-run')
    if ($null -eq $testRun) {
        throw 'Unexpected Unity Test Runner XML; cannot assert results.'
    }
    $executed = [int]$testRun.GetAttribute('testcasecount')
    $failed = [int]$testRun.GetAttribute('failed')
    $skipped = [int]$testRun.GetAttribute('skipped')
    $overall = $testRun.GetAttribute('result')
    Write-Host "Unity EditMode: total=$executed failed=$failed skipped=$skipped result=$overall"
    if ($executed -lt 8 -or $failed -ne 0 -or $skipped -ne 0 -or $overall -ne 'Passed') {
        throw 'EditMode result is not independently accepted; logs were preserved.'
    }
    Write-Host "Unity EditMode source tests passed at $sha. This is NOT a device test or art approval."
}
finally {
    Pop-Location
}
