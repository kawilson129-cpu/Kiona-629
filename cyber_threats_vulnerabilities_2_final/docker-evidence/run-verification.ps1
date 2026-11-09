$ErrorActionPreference='Stop'
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
$evidence='cyber_threats_vulnerabilities_2_final/docker-evidence'
$compose=@('compose','-p','derexi-ctv2','-f','cyber_threats_vulnerabilities_2_final/compose.yaml')
function Invoke-DockerEvidence($Name,$Arguments) {
    ("docker " + ($Arguments -join ' ')) | Add-Content "$evidence/commands.txt"
    & docker @Arguments > "$evidence/$Name.txt" 2>&1
    $code=$LASTEXITCODE
    "exit=$code" | Add-Content "$evidence/$Name.txt"
    if ($code -ne 0) { throw "Docker command failed: $Name ($code)" }
}
Invoke-DockerEvidence 'startup' ($compose+@('up','-d','--wait','--wait-timeout','120'))
Invoke-DockerEvidence 'self-test' ($compose+@('run','--rm','--no-deps','pulse-lab','--self-test'))
"Get-Content verify_container.py | docker compose ... exec -T pulse-lab python -" | Add-Content "$evidence/commands.txt"
Get-Content "$evidence/verify_container.py" -Raw | & docker @compose exec -T pulse-lab python - > "$evidence/container-checks.json" 2>&1
if ($LASTEXITCODE -ne 0) { throw 'Container checks failed' }
"Get-Content verify_feeds.py | docker compose ... exec -T pulse-lab python -" | Add-Content "$evidence/commands.txt"
Get-Content "$evidence/verify_feeds.py" -Raw | & docker @compose exec -T pulse-lab python - > "$evidence/container-feeds.json" 2>&1
"feed verification exit=$LASTEXITCODE" | Add-Content "$evidence/commands.txt"
Invoke-DockerEvidence 'services' ($compose+@('ps'))
$id=& docker @compose ps -q pulse-lab
& docker inspect $id > "$evidence/container-inspect.json"
& docker image inspect derexi-ctv2-pulse-lab > "$evidence/image-inspect.json"
Invoke-DockerEvidence 'logs' ($compose+@('logs','--no-color'))
