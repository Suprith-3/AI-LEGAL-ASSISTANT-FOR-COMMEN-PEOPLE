function Load-DotEnv {
    # Check if the .env file exists in the current directory
    if (-not (Test-Path -Path ".env")) {
        Write-Error "Error: .env file not found in the current directory."
        return
    }

    # Read all lines from the .env file
    $envLines = Get-Content -Path ".env"

    Write-Host "Loading environment variables from .env..."

    foreach ($line in $envLines) {
        # 1. Skip comments and empty lines
        if ($line.Trim() -match '^(#.*|\s*)$') {
            continue
        }

        # 2. Extract Key and Value: 
        #    - Looks for KEY=VALUE pattern
        #    - Handles optional quotes around the value
        if ($line -match '^\s*([a-zA-Z0-9_]+)\s*=\s*(.*)') {
            $key = $matches[1]
            $value = $matches[2].Trim()

            # Remove surrounding single or double quotes from the value
            if ($value -match '^"(.+)"$' -or $value -match "^'(.+)'$") {
                $value = $matches[1]
            }

            # Set the environment variable in the current session
            # $env: is the special PowerShell scope for environment variables
            $env:($key) = $value

            Write-Host "  -> Loaded $($key)"
        }
        else {
            Write-Warning "Skipping line (invalid format): $($line)"
        }
    }

    Write-Host "Done loading environment variables."
}