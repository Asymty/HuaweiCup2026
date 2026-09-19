$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    for ($pass = 1; $pass -le 2; $pass++) {
        Write-Host "Running XeLaTeX pass $pass/2..."
        & xelatex --disable-installer -interaction=nonstopmode -halt-on-error -file-line-error MathModel.tex
        if ($LASTEXITCODE -ne 0) {
            Write-Host "LATEX BUILD = FAIL"
            exit $LASTEXITCODE
        }
    }

    if (-not (Test-Path -LiteralPath ".\MathModel.log")) {
        Write-Error "MathModel.log was not generated."
        Write-Host "LATEX BUILD = FAIL"
        exit 2
    }

    $patterns = @(
        "Undefined reference",
        "Citation .* undefined",
        "multiply defined",
        "multiply-defined",
        "There were undefined references"
    )
    $issues = Select-String -Path ".\MathModel.log" -Pattern $patterns -CaseSensitive:$false
    if ($issues) {
        Write-Warning "Reference issues were found in MathModel.log:"
        $issues | ForEach-Object { Write-Warning $_.Line.Trim() }
        Write-Host "LATEX BUILD = PASS"
        Write-Host "REFERENCE CHECK = FAIL"
        exit 3
    }

    Write-Host "LATEX BUILD = PASS"
    Write-Host "REFERENCE CHECK = PASS"
    exit 0
}
finally {
    Pop-Location
}
