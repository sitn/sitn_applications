$destConfig = Read-Host -Prompt 'Input "prod", "prepub" or "local"'

# Do not deploy to internet with DEBUG set to True
$settings = Get-Content ("{0}\..\sitn\settings.py" -f $PSScriptRoot)
$isDebug = $settings | Select-String -Pattern "^\DEBUG = (True)$"
if ($isDebug.Matches.Success) {
    if (($destConfig -ne "local") -and ($destConfig -ne "dev")) {
        Write-Output "Cannot deploy if DEBUG=True in settings.py"
        Exit
    }
}
$envFile = ("{0}\..\.env.{1}" -f $PSScriptRoot, $destConfig)
# Read .env
foreach ($line in Get-Content $envFile) {
    $args_ = $line -split "="
    If ($args_[0] -And !$args_[0].StartsWith("#")) {
        $cmd = '$env:' + $args_[0].Trim('"') + '="' + $args_[1].Trim('"') + '"'
        Invoke-Expression $cmd
    }
}

$env:ENV_FILE = (".env.{0}" -f $destConfig)

if ($destConfig -eq "prod") {
    $env:DOCKER_HOST="ssh://root@nesitn3.ne.ch"
} elseif ($destConfig -eq "prepub") {
    $env:DOCKER_HOST="ssh://root@nesitn3.ne.ch"
} elseif ($destConfig -eq "dev") {
    $env:DOCKER_HOST="ssh://root@nesitnd3.ne.ch"
}

Write-Output ("{0} - DOCKER_PORT IS {1}" -f $(Get-Date -Format g), $env:DOCKER_PORT)

docker-compose build
docker-compose down
docker-compose up -d

foreach ($line in Get-Content $envFile) {
    $args_ = $line -split "="
    If ($args_[0] -And !$args_[0].StartsWith("#")) {
        $cmd = '$env:' + $args_[0].Trim('"') + '=""'
        Invoke-Expression $cmd
    }
}

$env:ENV_FILE = ""

Write-Output ("{0} - END" -f $(Get-Date -Format g))
