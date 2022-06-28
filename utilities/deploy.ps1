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
Write-Output ("{0} - DOCKER_PORT IS {1}" -f $(Get-Date -Format g), $env:DOCKER_PORT)
If (Test-Path 'env:DOCKER_HOST') { 
    Write-Output ("{0} - DOCKER_HOST IS {1}" -f $(Get-Date -Format g), $env:DOCKER_HOST)
} Else {
    Write-Output ("{0} - DOCKER_HOST IS NOT SET -> LOCAL DEPLOYMENT" -f $(Get-Date -Format g))
}

$env:ENV_FILE = (".env.{0}" -f $destConfig)

docker-compose build sitn_applications

docker-compose down
docker-compose up -d


foreach ($line in Get-Content $envFile) {
    $args_ = $line -split "="
    If ($args_[0] -And !$args_[0].StartsWith("#")) {
        $cmd = '$env:' + $args_[0].Trim('"') + '=""'
        Invoke-Expression $cmd
    }
}

Write-Output ("{0} - END" -f $(Get-Date -Format g))
