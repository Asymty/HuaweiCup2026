$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    $frontmatter = Join-Path $PSScriptRoot "frontmatter\frontmatter.pdf"
    $body = Join-Path $PSScriptRoot "BodyOnly.pdf"
    $output = Join-Path $PSScriptRoot "FinalPaper.pdf"

    if (-not (Test-Path -LiteralPath $frontmatter -PathType Leaf)) {
        Write-Host "FRONTMATTER PDF = MISSING"
        exit 2
    }
    if (-not (Test-Path -LiteralPath $body -PathType Leaf)) {
        Write-Host "BODY PDF = MISSING"
        exit 3
    }

    $tool = $null
    foreach ($candidate in @("qpdf", "pdfunite", "mutool")) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) {
            $tool = $candidate
            break
        }
    }

    if (-not $tool) {
        Write-Host "PDF MERGE TOOL = MISSING"
        exit 4
    }

    $tempOutput = Join-Path $PSScriptRoot ("FinalPaper.{0}.tmp.pdf" -f [Guid]::NewGuid().ToString("N"))
    try {
        switch ($tool) {
            "qpdf" {
                & qpdf --empty --pages $frontmatter $body -- $tempOutput
            }
            "pdfunite" {
                & pdfunite $frontmatter $body $tempOutput
            }
            "mutool" {
                & mutool merge -o $tempOutput $frontmatter $body
            }
        }

        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $tempOutput -PathType Leaf)) {
            Write-Host "PDF MERGE = FAIL"
            exit 5
        }

        Move-Item -LiteralPath $tempOutput -Destination $output -Force
        Write-Host ("PDF MERGE TOOL = {0}" -f $tool.ToUpperInvariant())
        Write-Host "PDF MERGE = PASS"
        Write-Host ("OUTPUT = {0}" -f $output)
        exit 0
    }
    finally {
        if (Test-Path -LiteralPath $tempOutput) {
            Remove-Item -LiteralPath $tempOutput -Force
        }
    }
}
finally {
    Pop-Location
}
