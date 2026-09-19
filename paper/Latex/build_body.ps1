$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    for ($pass = 1; $pass -le 2; $pass++) {
        Write-Host "Running BodyOnly XeLaTeX pass $pass/2..."
        & xelatex --disable-installer -interaction=nonstopmode -halt-on-error -file-line-error BodyOnly.tex
        if ($LASTEXITCODE -ne 0) {
            Write-Host "BODY LATEX BUILD = FAIL"
            exit $LASTEXITCODE
        }
    }

    if (-not (Test-Path -LiteralPath ".\BodyOnly.log")) {
        Write-Error "BodyOnly.log was not generated."
        Write-Host "BODY LATEX BUILD = FAIL"
        exit 2
    }

    $patterns = @(
        "Undefined reference",
        "Citation .* undefined",
        "multiply defined",
        "multiply-defined",
        "There were undefined references",
        "File .* not found",
        "Fatal error"
    )
    $issues = Select-String -Path ".\BodyOnly.log" -Pattern $patterns -CaseSensitive:$false
    if ($issues) {
        Write-Warning "Reference or build issues were found in BodyOnly.log:"
        $issues | ForEach-Object { Write-Warning $_.Line.Trim() }
        Write-Host "BODY LATEX BUILD = PASS"
        Write-Host "REFERENCE CHECK = FAIL"
        exit 3
    }

    Write-Host "BODY LATEX BUILD = PASS"
    Write-Host "REFERENCE CHECK = PASS"
    exit 0
}
finally {
    Pop-Location
}
