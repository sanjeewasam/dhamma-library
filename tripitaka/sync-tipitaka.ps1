# sync-tipitaka.ps1 - Windows/PowerShell version of sync-tipitaka.sh
#
# Pulls the Buddha Jayanti Tripitaka text from tipitaka.lk into .\static\text\
# and rebuilds manifest.json. The upstream text is CC BY-ND 4.0: copied verbatim,
# never edited. Report errors to path.nirvana@gmail.com, then re-run this.
#
# Usage (from the tripitaka folder):
#     powershell -ExecutionPolicy Bypass -File .\sync-tipitaka.ps1
# or, if your policy allows scripts:
#     .\sync-tipitaka.ps1
# Needs: git and python on PATH.

$ErrorActionPreference = "Stop"
$HERE       = Split-Path -Parent $MyInvocation.MyCommand.Path
$UPSTREAM   = "https://github.com/pathnirvana/tipitaka.lk.git"
$CACHE      = Join-Path $HERE ".cache\tipitaka.lk"
$SUBPATH    = "public/static/text"                    # git uses forward slashes
$SRC        = Join-Path $CACHE "public\static\text"    # filesystem path
$DEST       = Join-Path $HERE "static\text"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git not found on PATH. Install Git for Windows." }
$py = $null
foreach ($c in @("python","python3","py")) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) { throw "python not found on PATH. Install Python 3." }

New-Item -ItemType Directory -Force -Path (Join-Path $HERE ".cache") | Out-Null
New-Item -ItemType Directory -Force -Path $DEST | Out-Null

if (-not (Test-Path (Join-Path $CACHE ".git"))) {
  Write-Host "-> First run: cloning upstream (sparse, no blobs)..."
  git clone --filter=blob:none --sparse $UPSTREAM $CACHE
  git -C $CACHE sparse-checkout set $SUBPATH "public/static/data"
} else {
  Write-Host "-> Fetching upstream updates..."
  $branch = (git -C $CACHE rev-parse --abbrev-ref HEAD).Trim()
  git -C $CACHE fetch --filter=blob:none origin
  git -C $CACHE sparse-checkout set $SUBPATH "public/static/data"
  git -C $CACHE reset --hard "origin/$branch"
}

if (-not (Test-Path $SRC)) { throw "Upstream text folder not materialised at $SRC. Delete .cache and re-run." }

Write-Host "-> Copying *.json into $DEST (mirroring upstream)..."
Get-ChildItem -Path $DEST -Filter *.json -ErrorAction SilentlyContinue | Remove-Item -Force
Copy-Item -Path (Join-Path $SRC "*.json") -Destination $DEST -Force
$count = (Get-ChildItem -Path $DEST -Filter *.json).Count
Write-Host "   $count text files synced."

Write-Host "-> Building navigation index (books.json)..."
& $py (Join-Path $HERE "build-manifest.py") --root $HERE --tree (Join-Path $CACHE "public\static\data\tree.json")

Write-Host "OK. Review, then:  git add tripitaka; git commit -m 'Sync Tripitaka'; git push"
