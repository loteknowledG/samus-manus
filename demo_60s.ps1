# 60s hands‑free demo for Warp + hands.py + pyautogui
$ErrorActionPreference = 'Stop'

$demoOut = 'C:\dev\samus-manus\demo_60s.png'

# 1) Open Notepad and type a message
Start-Process notepad
Start-Sleep -Seconds 1
python C:\dev\samus-manus\hands.py type 'AI with agency — powered by Warp + Python' --interval 0.02
python C:\dev\samus-manus\hands.py press enter
python C:\dev\samus-manus\hands.py type 'Now opening Paint and drawing...'

# 2) Open Paint and maximize
Start-Process mspaint
Start-Sleep -Seconds 1.5
python -c 'import pyautogui,time; import time as t; pyautogui.keyDown("alt"); pyautogui.press("space"); pyautogui.keyUp("alt"); t.sleep(0.2); pyautogui.press("x")'

# 3) Draw a rectangle relatively to screen size
python -c 'import pyautogui as p; w,h=p.size(); x1,y1=int(w*0.35), int(h*0.45); x2,y2=int(w*0.65), int(h*0.75); p.moveTo(x1,y1); p.mouseDown(); p.dragTo(x2,y1, duration=0.25); p.dragTo(x2,y2, duration=0.25); p.dragTo(x1,y2, duration=0.25); p.dragTo(x1,y1, duration=0.25); p.mouseUp()'

# 4) Screenshot proof
python C:\dev\samus-manus\hands.py screenshot --out $demoOut
Write-Host ("Saved: {0}" -f $demoOut)
