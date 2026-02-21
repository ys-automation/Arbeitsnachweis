param(
  [string]$SourceDir = "web_arbeitsnachweis",
  [string]$OutputZip = "web_arbeitsnachweis_paket.zip"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([System.IO.Path]::IsPathRooted($SourceDir)) {
  $sourcePath = (Resolve-Path $SourceDir).Path
} else {
  $sourcePath = (Resolve-Path (Join-Path $repoRoot $SourceDir)).Path
}

if ([System.IO.Path]::IsPathRooted($OutputZip)) {
  $outputPath = $OutputZip
} else {
  $outputPath = Join-Path $repoRoot $OutputZip
}

if (-not (Test-Path $sourcePath -PathType Container)) {
  throw "Source directory not found: $sourcePath"
}

if (Test-Path $outputPath) {
  Remove-Item $outputPath -Force
}

Compress-Archive -Path (Join-Path $sourcePath "*") -DestinationPath $outputPath -CompressionLevel Optimal

$artifact = Get-Item $outputPath
Write-Host "Release ZIP created: $($artifact.FullName)"
Write-Host "Size (bytes): $($artifact.Length)"
