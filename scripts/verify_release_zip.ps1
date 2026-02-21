param(
  [string]$SourceDir = "web_arbeitsnachweis",
  [string]$ZipPath = "web_arbeitsnachweis_paket.zip"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([System.IO.Path]::IsPathRooted($SourceDir)) {
  $sourcePath = (Resolve-Path $SourceDir).Path
} else {
  $sourcePath = (Resolve-Path (Join-Path $repoRoot $SourceDir)).Path
}

if ([System.IO.Path]::IsPathRooted($ZipPath)) {
  $zipFilePath = (Resolve-Path $ZipPath).Path
} else {
  $zipFilePath = (Resolve-Path (Join-Path $repoRoot $ZipPath)).Path
}

if (-not (Test-Path $sourcePath -PathType Container)) {
  throw "Source directory not found: $sourcePath"
}

if (-not (Test-Path $zipFilePath -PathType Leaf)) {
  throw "ZIP file not found: $zipFilePath"
}

$zip = [System.IO.Compression.ZipFile]::OpenRead($zipFilePath)
$zipMap = @{}
foreach ($entry in $zip.Entries) {
  $zipMap[$entry.FullName] = $entry
}

$diffs = @()
Get-ChildItem -Path $sourcePath -Recurse -File | ForEach-Object {
  $rel = $_.FullName.Substring($sourcePath.Length + 1)

  if (-not $zipMap.ContainsKey($rel)) {
    $diffs += [pscustomobject]@{
      File = $rel
      Status = "MissingInZip"
    }
    return
  }

  $entry = $zipMap[$rel]
  $tmp = [System.IO.Path]::GetTempFileName()

  $entryStream = $entry.Open()
  $tmpStream = [System.IO.File]::OpenWrite($tmp)
  $entryStream.CopyTo($tmpStream)
  $entryStream.Dispose()
  $tmpStream.Dispose()

  $zipHash = (Get-FileHash -Path $tmp -Algorithm SHA256).Hash
  Remove-Item $tmp -Force
  $localHash = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash

  if ($zipHash -ne $localHash) {
    $diffs += [pscustomobject]@{
      File = $rel
      Status = "ContentDiff"
    }
  }
}

foreach ($name in $zipMap.Keys) {
  $localPath = Join-Path $sourcePath $name
  if (-not (Test-Path $localPath -PathType Leaf)) {
    $diffs += [pscustomobject]@{
      File = $name
      Status = "ExtraInZip"
    }
  }
}

$zip.Dispose()

if ($diffs.Count -gt 0) {
  Write-Host "ZIP verification failed. Differences detected:"
  $diffs | Sort-Object Status, File | Format-Table -AutoSize | Out-String | Write-Host
  throw "ZIP does not match source folder."
}

$count = (Get-ChildItem -Path $sourcePath -Recurse -File).Count
Write-Host "ZIP_OK: no diffs"
Write-Host "Verified files: $count"
