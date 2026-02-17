param(
  [ValidateSet('smiley','house','both')]
  [string]$What = 'smiley',
  [string]$Label = 'warp-jump',
  [string]$App = 'mspaint',
  [string]$OutDir = '.'
)

$ErrorActionPreference = 'Stop'

# Announce + draw with snaps + log
python "$PSScriptRoot\tools\warp_jump.py" --what $What --label $Label --app $App --outdir $OutDir
