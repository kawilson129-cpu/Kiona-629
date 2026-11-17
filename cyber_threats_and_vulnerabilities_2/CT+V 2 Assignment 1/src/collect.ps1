$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = (Resolve-Path (Join-Path $taskRoot '../..')).Path
$out = Join-Path $taskRoot 'evidence'
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$run = Join-Path $out $stamp
New-Item -ItemType Directory -Force $run | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Save-Json($name, $value) {
    [IO.File]::WriteAllText((Join-Path $run $name), (ConvertTo-Json -InputObject $value -Depth 20), $utf8)
}
$packages = @(Get-ChildItem (Join-Path $repoRoot 'derexi-policy-pilot/.venv/Lib/site-packages') -Directory -Filter '*.dist-info' | ForEach-Object {
    $metadata = Join-Path $_.FullName 'METADATA'
    $lines = Get-Content -LiteralPath $metadata
    $name = ($lines | Where-Object { $_ -match '^Name: ' } | Select-Object -First 1) -replace '^Name: ', ''
    $version = ($lines | Where-Object { $_ -match '^Version: ' } | Select-Object -First 1) -replace '^Version: ', ''
    $installer = Join-Path $_.FullName 'INSTALLER'
    [ordered]@{name=$name; version=$version; requires=@($lines | Where-Object { $_ -match '^Requires-Dist: ' } | ForEach-Object { $_ -replace '^Requires-Dist: ', '' }); metadata_sha256=(Get-FileHash $metadata -Algorithm SHA256).Hash.ToLower(); installer=$(if(Test-Path $installer){(Get-Content $installer -Raw).Trim()}else{'unknown'}); direct_url_present=(Test-Path (Join-Path $_.FullName 'direct_url.json')); record_present=(Test-Path (Join-Path $_.FullName 'RECORD'))}
})
Save-Json 'inventory.json' ([ordered]@{generated_at=[DateTime]::UtcNow.ToString('o'); method='Read distribution metadata only; no imports, installs, app calls or environment secrets'; packages=$packages})
$inputs = @(
 'cyber_threats_and_vulnerabilities_2/Cyber Threats and Vulnerabilities 2 Tasks.pdf',
 'cyber_threats_and_vulnerabilities_1/CT+V Assignment 1/DeRexi_APT38_FASTCash_Incident_MITRE_Report.pdf',
 'cyber_threats_and_vulnerabilities_1/CT+V Assignment 1/Malware_Analysis_Threat_Dossier_k_php.pdf',
 'cyber_threats_and_vulnerabilities_1/CT+V Assignment 2/DeRexi_Vulnerability_Assessment_Report.pdf',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/closure/advisories/assessment.json',
 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/control-assessment.md',
 'derexi-policy-pilot/requirements.txt','derexi-policy-pilot/requirements-dev.txt',
 'derexi-policy-pilot/backend/security.py','derexi-policy-pilot/backend/main.py',
 'derexi-policy-pilot/backend/pulse/service.py','derexi-policy-pilot/backend/pulse/sources.py',
 'derexi-policy-pilot/backend/ai.py','derexi-policy-pilot/backend/static/index.html',
 'derexi-policy-pilot/backend/tests/test_week9_security.py',
 'semester_5/DeRexi_Week 11/evidence/final-integration-20261112/security-results.json',
 'semester_5/DeRexi_Week 11/evidence/final-integration-20261112/pulse-results.json'
)
$hashes = @($inputs | ForEach-Object { $p=Join-Path $repoRoot $_; [ordered]@{path=$_; sha256=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower()} })
Save-Json 'source-hashes.json' $hashes
$results = New-Object System.Collections.Generic.List[object]
function Check($id, $status, $actual) { $results.Add([ordered]@{id=$id;status=$status;actual=$actual}) }
Check 'INV-01' $(if($packages.Count -gt 0){'PASS'}else{'FAIL'}) "$($packages.Count) distributions read without importing packages"
$req = Get-Content (Join-Path $repoRoot 'derexi-policy-pilot/requirements.txt') -Raw
Check 'SC-LOCK' $(if($req -match 'fastapi==[0-9]' -and $req -match '--hash=sha256:'){'PASS'}else{'FAIL'}) 'Runtime requirements contain lower bounds and no complete hash lock'
$prior = Get-Content (Join-Path $repoRoot 'cyber_threats_and_vulnerabilities_2/CT+V 2 Assignment 2/closure/advisories/assessment.json') -Raw | ConvertFrom-Json
$matches = @($prior.packages | Where-Object { @($_.vulnerabilities).Count -gt 0 } | ForEach-Object {
    $old=$_; $current=@($packages | Where-Object { $_.name -eq $old.name })
    [ordered]@{name=$old.name; prior_version=$old.version; current_version=@($current | ForEach-Object {$_.version}); same_version=($current.Count -eq 1 -and $current[0].version -eq $old.version); advisory_ids=@($old.vulnerabilities | ForEach-Object {$_.id}); scope='Historical registry match; current version comparison, not exploit verification'}
})
Save-Json 'historical-advisory-comparison.json' $matches
foreach($m in $matches){ Check ('SC-ADVISORY-'+$m.name) $(if($m.same_version){'FAIL'}else{'BLOCKED'}) ($m | ConvertTo-Json -Compress) }
foreach($suite in @('security','pulse')) {
    $p=Join-Path $repoRoot "semester_5/DeRexi_Week 11/evidence/final-integration-20261112/$suite-results.json"
    $data=Get-Content $p -Raw | ConvertFrom-Json
    Check ('PRIOR-'+$suite) $(if($data.failed -eq 0){'PASS'}else{'FAIL'}) "Reused November 12 record: $($data.passed) pass / $($data.failed) fail; NOT rerun"
}
Check 'LIVE-SECURITY' 'BLOCKED' 'No current production/runtime verification authorized or performed; prior isolated tests cannot prove live protection'
Check 'MALWARE-ORIGINAL' 'BLOCKED' 'No authorized raw sample identified; secondary published technical analysis selected'
Check 'PROVENANCE' 'BLOCKED' 'INSTALLER/RECORD metadata is not cryptographic publisher provenance; original wheel attestations absent'
$tracked = @(& git -C $repoRoot ls-files -- '*.php' '*.bin' '*.elf' '*.dll' '*.so' '*.exe')
Save-Json 'sample-search.json' ([ordered]@{method='git ls-files known binary/script extensions plus prior rg --files review; excludes ignored/untracked locations and archives'; candidates=$tracked; conclusion='No raw sample identified in reviewed coursework; not an exhaustive filesystem forensic search'})
Save-Json 'results.json' ([ordered]@{generated_at=[DateTime]::UtcNow.ToString('o'); command='powershell -NoProfile -ExecutionPolicy Bypass -File src/collect.ps1'; checks=$results; pass=@($results | Where-Object {$_.status -eq 'PASS'}).Count; fail=@($results | Where-Object {$_.status -eq 'FAIL'}).Count; blocked=@($results | Where-Object {$_.status -eq 'BLOCKED'}).Count})
[IO.File]::WriteAllText((Join-Path $out 'latest-run.txt'), $stamp, $utf8)
Write-Output "$stamp : $($packages.Count) packages; $($results.Count) recorded outcomes. See results.json."
