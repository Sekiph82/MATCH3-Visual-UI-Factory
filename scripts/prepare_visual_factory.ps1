# MATCH3 VUF safe local checkout preparation (no destructive operations).
[CmdletBinding()]
param(
    [switch]$FetchAndFastForward,
    [switch]$OpenUnity
)
$ErrorActionPreference = 'Stop'
$project = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$expected = 'Sekiph82/MATCH3-Visual-UI-Factory'
if (!(Test-Path -LiteralPath (Join-Path $project 'Packages/manifest.json'))) {
    throw "This script must be run from the existing MATCH3 Visual Factory checkout."
}
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is not installed or not on PATH.'
}
Push-Location -LiteralPath $project
try {
    $remote = (& git remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0 -or $remote -notmatch '(?i)(github\.com[:/])Sekiph82/MATCH3-Visual-UI-Factory(\.git)?$') {
        throw "Unexpected Git remote '$remote'; no sync attempted."
    }
    $branch = (& git branch --show-current).Trim()
    if ($branch -ne 'main') { throw "Current branch '$branch' is not main. No sync attempted." }
    $dirty = @(& git status --porcelain=v1 --untracked-files=normal)
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect Git status.' }
    if ($dirty.Count -gt 0) {
        throw "Local modified/untracked files present ($($dirty.Count)). No automatic sync; inspect/preserve them first."
    }
    Write-Host "Existing checkout verified: $project"
    if ($FetchAndFastForward) {
        & git fetch --no-tags origin main
        if ($LASTEXITCODE -ne 0) { throw 'Git fetch failed. Local files remain unchanged.' }
        $counts = (& git rev-list --left-right --count 'HEAD...origin/main').Trim() -split '\s+'
        if ($LASTEXITCODE -ne 0 -or $counts.Count -ne 2) {
            throw 'Cannot determine local/remote divergence. No merge attempted.'
        }
        $ahead = [int]$counts[0]
        $behind = [int]$counts[1]
        if ($ahead -ne 0) {
            throw "Checkout has $ahead local-only commits. No automatic merge or reset."
        }
        if ($behind -gt 0) {
            & git merge --ff-only origin/main
            if ($LASTEXITCODE -ne 0) { throw 'Fast-forward failed. No force/reset attempted.' }
        }
        $local = (& git rev-parse HEAD).Trim()
        $origin = (& git rev-parse origin/main).Trim()
        if ($local -ne $origin) { throw 'Post-sync HEAD differs from origin/main.' }
        Write-Host "Verified synced SHA: $local"
    }
    $file = Join-Path $project 'ProjectSettings/ProjectVersion.txt'
    $version = Get-Content -LiteralPath $file -Raw
    if ($version -notmatch 'm_EditorVersion:\s*6000\.6\.5f1') {
        throw 'Unexpected Unity project Editor version.'
    }
    Write-Host 'Unity project version pinned to 6000.6.5f1'
    if ($OpenUnity) {
        $editor = Join-Path ${env:ProgramFiles} 'Unity/Hub/Editor/6000.6.5f1/Editor/Unity.exe'
        if (!(Test-Path -LiteralPath $editor)) {
            throw "Unity 6000.6.5f1 not found at standard install location: $editor. Use Unity Hub Add Project manually."
        }
        Write-Host 'Opening existing Unity project; no clone or cache cleanup.'
        Start-Process -FilePath $editor -ArgumentList @('-projectPath', ('"' + $project + '"'))
    }
} finally {
    Pop-Location
}
