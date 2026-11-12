# Read-only documentation checks; writes only this Week 11 result file.
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$week = Join-Path $repo 'semester_5/DeRexi_Week 11'
$documents = @((Join-Path $repo 'derexi-policy-pilot/README.md'), (Join-Path $repo 'derexi-policy-pilot/docs/deployment.md'))
$documents += @(Get-ChildItem -LiteralPath $week -Filter '*.md' -Recurse | ForEach-Object { $_.FullName })
$results = New-Object System.Collections.Generic.List[object]
function Record($name, $pass, $detail) {
    $results.Add([pscustomobject]@{check=$name; result=$(if($pass){'PASS'}else{'FAIL'}); detail=$detail})
}
$links = 0
foreach ($file in $documents) {
    $body = [IO.File]::ReadAllText($file)
    $relative = $file.Substring($repo.Length + 1).Replace('\','/')
    Record "fences: $relative" (([regex]::Matches($body, '(?m)^```').Count % 2) -eq 0) 'Balanced fenced code blocks'
    foreach ($m in [regex]::Matches($body, '\]\(([^)]+)\)')) {
        $target = $m.Groups[1].Value
        if ($target -match '^(https?://|#)') { continue }
        $target = [Uri]::UnescapeDataString(($target -split '#')[0])
        $resolved = [IO.Path]::GetFullPath((Join-Path (Split-Path $file -Parent) $target))
        $links++
        Record "link: $relative -> $target" (Test-Path -LiteralPath $resolved) 'Local target exists; external URLs not contacted'
    }
    foreach ($m in [regex]::Matches($body, '(?s)```powershell\r?\n(.*?)```')) {
        $tokens = $null
        $errors = $null
        [Management.Automation.Language.Parser]::ParseInput($m.Groups[1].Value, [ref]$tokens, [ref]$errors) | Out-Null
        Record "PowerShell syntax: $relative" ($errors.Count -eq 0) 'Parsed only; commands were not executed'
    }
}
foreach ($target in @('derexi-policy-pilot/requirements.txt','derexi-policy-pilot/requirements-dev.txt','derexi-policy-pilot/backend/.env.example','derexi-policy-pilot/backend/main.py','derexi-policy-pilot/backend/tests/serve_week10_fixture.py','derexi-policy-pilot/backend/migrations/2026-11-10_week8_governance.sql','derexi-policy-pilot/backend/migrations/2026-11-10_week8_owner_seed.sql')) {
    Record "setup path: $target" (Test-Path -LiteralPath (Join-Path $repo $target)) 'Required documented source/configuration template exists'
}
$entry = [IO.File]::ReadAllText((Join-Path $repo 'derexi-policy-pilot/backend/tests/serve_week10_fixture.py'))
Record 'Fixture import target' ($entry.Contains('import serve_week9_fixture as fixture')) 'Import-based uvicorn target resolves fixture.main.app through existing source; not imported/executed'
$main = [IO.File]::ReadAllText((Join-Path $repo 'derexi-policy-pilot/backend/main.py'))
Record 'API health implementation' ($main.Contains('"database": "reachable"')) 'Documented health outcome matches existing source'
$dev = [IO.File]::ReadAllText((Join-Path $repo 'derexi-policy-pilot/backend/dev_auth.py'))
Record 'Persona boundary source' ($dev.Contains('Development identity is loopback-only') -and $dev.Contains('same origin')) 'Existing loopback and same-origin guards unchanged'
$htmlFiles = @(Get-ChildItem -LiteralPath (Join-Path $repo 'derexi-policy-pilot/backend/static') -Filter '*.html')
$badHtml = @()
foreach ($html in $htmlFiles) {
    $visible = [regex]::Replace([IO.File]::ReadAllText($html.FullName), '(?s)<!--.*?-->', '')
    if ($visible -match '(?i)\b(SDLC|classroom|fixture|semester|capstone|Week\s+\d+)\b') { $badHtml += $html.Name }
}
Record 'Normal HTML terminology' ($badHtml.Count -eq 0) 'No classroom/SDLC/fixture labels in HTML after comment removal; dynamic JS separately reviewed'
$summary = [ordered]@{
    date='2026-11-11'; scope='Documentation/source inspection only; no application imports, servers, network, DB calls, installation or regression tests'
    documents=$documents.Count; local_links=$links
    passed=@($results | Where-Object result -eq 'PASS').Count
    failed=@($results | Where-Object result -eq 'FAIL').Count
    checks=$results
}
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'documentation-checks.json') -Encoding UTF8
Write-Output ("Documents {0}; local links {1}; PASS {2}; FAIL {3}" -f $summary.documents,$links,$summary.passed,$summary.failed)
$results | Where-Object result -eq 'FAIL' | Format-Table -AutoSize
if ($summary.failed -gt 0) { exit 1 }
