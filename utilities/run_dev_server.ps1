foreach ($line in Get-Content $PSScriptRoot\..\.env.dev) {
    $args = $line -split "="
    If ($args[0] -And !$args[0].StartsWith("#")) {
        $cmd = '$env:' + $args[0].Trim('"') + '="' + $args[1].Trim('"') + '"'
        Invoke-Expression $cmd
    }
}

..\venv\Scripts\python.exe ..\manage.py runserver 8081
