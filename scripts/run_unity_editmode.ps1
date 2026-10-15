# Unity 6000.6.5f1 local EditMode source tests, no GitHub Actions, no deletes.
# Nothing executes until the owner runs this script on the existing project.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EvidenceDirectory,
    [string]$UnityExe = '',
    [string]$ExpectedUntrackedManifest = ''
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
    if ($LASTEXITCODE -ne 0) {
        throw 'Cannot inspect local checkout status.'
    }
    $trackedDirty = @($dirty | Where-Object { -not $_.StartsWith('?? ') })
    if ($trackedDirty.Count -gt 0) {
        throw 'Tracked checkout changes are present; preserve/inspect them before running.'
    }
    $untrackedPaths = @($dirty | Where-Object { $_.StartsWith('?? ') } |
        ForEach-Object { $_.Substring(3).Replace('\', '/') })
    if ($untrackedPaths.Count -gt 0 -or -not [string]::IsNullOrWhiteSpace($ExpectedUntrackedManifest)) {
        if ([string]::IsNullOrWhiteSpace($ExpectedUntrackedManifest)) {
            throw 'Untracked checkout files require an external SHA-256 manifest; preserve/inspect them before running.'
        }
        $manifestPath = [IO.Path]::GetFullPath($ExpectedUntrackedManifest)
        if ($manifestPath.StartsWith($project + [IO.Path]::DirectorySeparatorChar,
                                     [StringComparison]::OrdinalIgnoreCase) -or
            -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
            throw 'Expected untracked manifest must be an existing file outside the project checkout.'
        }
        try {
            $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
            $entries = @($manifest.files)
            $manifestPaths = @($entries | ForEach-Object { [string]$_.path })
        }
        catch {
            throw 'Expected untracked manifest is not valid JSON with a files array.'
        }
        if ($manifestPaths.Count -ne $untrackedPaths.Count -or
            @($untrackedPaths | Where-Object { $_ -notin $manifestPaths }).Count -gt 0 -or
            @($manifestPaths | Group-Object | Where-Object Count -gt 1).Count -gt 0) {
            throw 'Untracked files do not exactly match the external SHA-256 manifest.'
        }
        foreach ($entry in $entries) {
            $relativePath = ([string]$entry.path).Replace('/', [IO.Path]::DirectorySeparatorChar)
            if ([IO.Path]::IsPathRooted($relativePath) -or
                $relativePath.Split([IO.Path]::DirectorySeparatorChar) -contains '..' -or
                [string]$entry.sha256 -notmatch '^[0-9a-fA-F]{64}$') {
                throw 'Expected untracked manifest contains an unsafe path or invalid SHA-256.'
            }
            $artifactPath = [IO.Path]::GetFullPath((Join-Path $project $relativePath))
            if (-not $artifactPath.StartsWith($project + [IO.Path]::DirectorySeparatorChar,
                                               [StringComparison]::OrdinalIgnoreCase) -or
                -not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) {
                throw "Expected Unity-generated file is missing or outside the project: $($entry.path)"
            }
            $artifact = Get-Item -LiteralPath $artifactPath -Force
            if ($artifact.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Expected Unity-generated file is a reparse point: $($entry.path)"
            }
            $actualHash = (Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256).Hash
            if ($actualHash -ne [string]$entry.sha256) {
                throw "Expected Unity-generated file hash changed: $($entry.path)"
            }
        }
        Write-Host "Preserving $($untrackedPaths.Count) external-manifest-verified Unity import files."
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
        '-batchmode', '-nographics',
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
