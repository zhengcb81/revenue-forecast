# finalize_self.ps1 — hash every deliverable of this attempt into evidence/self_manifest.json (pure ASCII source)
$ErrorActionPreference = 'Stop'
$HERE = $PSScriptRoot
$ATTEMPT = Split-Path $HERE
$sha = [System.Security.Cryptography.SHA256]::Create()
$rows = @()
foreach ($f in @(Get-ChildItem $ATTEMPT -Recurse -File | Where-Object { $_.FullName -notmatch 'self_manifest\.json' } | Sort-Object FullName)) {
  $rel = $f.FullName.Substring($ATTEMPT.Length + 1) -replace '\\', '/'
  $h = (($sha.ComputeHash([IO.File]::ReadAllBytes($f.FullName))) | ForEach-Object { $_.ToString('x2') }) -join ''
  $rows += [pscustomobject]@{ file = $rel; sha256 = $h; bytes = $f.Length }
}
$json = [pscustomobject]@{
  card_id        = 'M-T-REVIEW'
  attempt_id     = 'a20260923-01'
  generated_utc  = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
  note           = 'self-manifest of all deliverables at finalization; verifier: re-hash and compare'
  file_count     = $rows.Count
  files          = $rows
}
$json | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path (Join-Path $ATTEMPT 'evidence') 'self_manifest.json') -Encoding UTF8
Write-Output ('self_manifest: {0} files' -f $rows.Count)
