# Workaround for "Failed to scan for dependencies" when project path contains spaces (e.g. "mentee_tracker_mca - Copy").
# Run this script from the frontend folder, then open http://localhost:3000
$projectRoot = (Get-Item $PSScriptRoot).Parent.FullName
$driveLetter = "V:"
Write-Host "Mapping $driveLetter to $projectRoot (path without spaces for Vite)..."
subst $driveLetter $projectRoot
Set-Location "$driveLetter\frontend"
try {
  npm start
} finally {
  subst $driveLetter /d
  Write-Host "Unmapped $driveLetter"
}
