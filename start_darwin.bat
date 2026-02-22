@echo off
echo Project Darwin v17 - FULL EXPLICIT ACCESS
echo Every file in core, pages, .streamlit now loaded
echo Leave this window open forever

:loop
echo %date% %time% - New evolution cycle starting...

cd /d C:\Users\Harry\moonshotv2
git pull origin main --rebase --autostash

aider ^
  --model openrouter/deepseek/deepseek-r1 ^
  --edit-format whole ^
  --yes ^
  --auto-commits ^
  --message-file darwin_system_prompt.txt ^
  streamlit_app.py ^
  worker.py ^
  requirements.txt ^
  .env.example ^
  README.md ^
  .streamlit/config.toml ^
  core/__init__.py ^
  core/causal_engine.py ^
  core/data_fetcher.py ^
  core/evo_factory.py ^
  core/liquidity_teleporter.py ^
  core/omniverse.py ^
  core/registry.py ^
  core/shadow_crowd.py ^
  pages/01_ShadowCrowd_Oracle.py ^
  pages/02_CausalForge_Engine.py ^
  pages/03_Financial_Omniverse.py ^
  pages/04_EvoAlpha_Factory.py ^
  pages/05_Liquidity_Teleporter.py ^
  pages/06_Impact_Dashboard.py ^
  pages/07_Live_Alpha_Execution_Lab.py

git push origin main

echo %date% %time% - Cycle finished. Sleeping 2 minutes...
timeout /t 120 /nobreak >nul
goto loop