@echo off
echo ========================================================
echo   Darwin - ONE-TIME CLEANUP FOR JOSEPH DEMO
echo   Fixes everything then stops completely
echo ========================================================

cd /d C:\Users\Harry\moonshotv2

aider ^
  --model openrouter/deepseek/deepseek-r1 ^
  --edit-format whole ^
  --yes ^
  --auto-commits ^
  --message-file darwin_system_prompt.txt ^
  .

git push origin main

echo.
echo ========================================================
echo   CLEANUP COMPLETE - APP IS READY FOR JOSEPH
echo   Close this window.
echo   Redeploy your app and show Joseph.
echo ========================================================
pause