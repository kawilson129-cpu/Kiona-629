$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = (Resolve-Path (Join-Path $taskRoot '../..')).Path
$runName = (Get-Content (Join-Path $taskRoot 'evidence/latest-run.txt') -Raw).Trim()
$run = Join-Path $taskRoot "evidence/$runName"
$checks = New-Object System.Collections.Generic.List[object]
function Check($name, $ok) { $checks.Add([ordered]@{name=$name;status=$(if($ok){'PASS'}else{'FAIL'})}) }
$inventory = Get-Content (Join-Path $run 'inventory.json') -Raw | ConvertFrom-Json
$results = Get-Content (Join-Path $run 'results.json') -Raw | ConvertFrom-Json
$hashes = Get-Content (Join-Path $run 'source-hashes.json') -Raw | ConvertFrom-Json
$comparison = Get-Content (Join-Path $run 'historical-advisory-comparison.json') -Raw | ConvertFrom-Json
Check 'Nonempty installed inventory' (@($inventory.packages).Count -gt 0)
Check 'Unique package identities' ((@($inventory.packages.name | Sort-Object -Unique).Count) -eq @($inventory.packages).Count)
foreach($entry in $hashes){ Check ('Source unchanged: '+$entry.path) ((Get-FileHash -LiteralPath (Join-Path $repoRoot $entry.path) -Algorithm SHA256).Hash.ToLower() -eq $entry.sha256) }
$rubric = @($hashes | Where-Object {$_.path -like '*Tasks.pdf'})
Check 'Official rubric identity matches prior visual evidence' ($rubric.Count -eq 1 -and $rubric[0].sha256 -eq '5961118200fea38c10c2e9cf1d4aa6685c6f5750ddbcc44082c5ebcd9351f07b')
$metadata = @(Get-ChildItem (Join-Path $repoRoot 'derexi-policy-pilot/.venv/Lib/site-packages') -Filter '*.dist-info' -Directory | ForEach-Object { (Get-FileHash (Join-Path $_.FullName 'METADATA') -Algorithm SHA256).Hash.ToLower() })
foreach($pkg in $inventory.packages){ Check ('Metadata fingerprint: '+$pkg.name) ($metadata -contains $pkg.metadata_sha256) }
foreach($state in @('PASS','FAIL','BLOCKED')) {
    $key=$state.ToLower()
    Check ('Outcome count '+$state) (@($results.checks | Where-Object {$_.status -eq $state}).Count -eq $results.$key)
}
Check 'Two historical advisory package matches retained' ($comparison.Count -eq 2)
foreach($item in $comparison) {
    $current = @($inventory.packages | Where-Object {$_.name -eq $item.name})
    Check ('Advisory version equality: '+$item.name) ($current.Count -eq 1 -and $current[0].version -eq $item.current_version[0] -and $item.same_version -eq ($current[0].version -eq $item.prior_version))
}
$required=@('README.md','docs/rubric-checklist.md','docs/implementation.md','docs/apt-campaign-analysis.md','docs/malware-analysis.md','docs/zero-day-research.md','docs/supply-chain-assessment.md','docs/final-summary.md','docs/progress.md')
foreach($path in $required){ Check ('Deliverable exists: '+$path) (Test-Path -LiteralPath (Join-Path $taskRoot $path)) }
foreach($file in Get-ChildItem $taskRoot -Recurse -File -Filter '*.md') {
    $body=Get-Content $file.FullName -Raw
    foreach($match in [regex]::Matches($body,'\[[^\]]+\]\(([^)]+)\)')) {
        $target=$match.Groups[1].Value
        if($target -match '^(https?://|#)'){continue}
        $target=[Uri]::UnescapeDataString(($target -split '#')[0])
        Check ('Local link: '+$file.Name+' -> '+$target) (Test-Path -LiteralPath (Join-Path $file.DirectoryName $target))
    }
}
$failed=@($checks | Where-Object {$_.status -eq 'FAIL'}).Count
$stamp=[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$output=[ordered]@{generated_at=[DateTime]::UtcNow.ToString('o');collector_run=$runName;scope='Artifact consistency only; no application execution';passed=$checks.Count-$failed;failed=$failed;checks=$checks}
$utf8=New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText((Join-Path $taskRoot "evidence/validation-$stamp.json"), (ConvertTo-Json -InputObject $output -Depth 8), $utf8)
Write-Output "$($checks.Count-$failed) PASS / $failed FAIL (artifact consistency)"
if($failed){ $checks | Where-Object {$_.status -eq 'FAIL'} | ConvertTo-Json -Compress; exit 1 }
