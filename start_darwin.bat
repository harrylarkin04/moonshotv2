@echo off
echo === Project Darwin - One-Time Cleanup Mode for Joseph demo ===
echo It will fix everything and then stop
echo Leave open until you see "CLEANUP COMPLETE"

:loop
echo %date% %time% - Cleanup cycle starting...

cd /d C:\Users\Harry\moonshotv2
git pull origin main --rebase --autostash

aider ^
  --model openrouter/deepseek/deepseek-r1 ^
  --edit-format whole ^
  --yes ^
  --auto-commits ^
  --message-file darwin_system_prompt.txt ^
  .

git push origin main

echo %date% %time% - Cycle complete.
timeout /t 180 /nobreak >nul
goto loop