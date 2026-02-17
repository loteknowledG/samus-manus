param(
  [Parameter(Mandatory=$true, Position=0)]
  [string]$Text,
  [int]$Rate
)

$ErrorActionPreference = 'SilentlyContinue'
$py = (Get-Command python).Source
if ($Rate) {
  & $py "$PSScriptRoot\tools\tts_say.py" --ensure --rate $Rate -- "%Text%"
} else {
  & $py "$PSScriptRoot\tools\tts_say.py" --ensure -- "%Text%"
}
