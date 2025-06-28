@echo off
echo 🚀 Setting up AVScript AI Chatbot for Windows...

python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r backend\requirements.txt

mkdir data 2>nul
mkdir config 2>nul
mkdir vector_index 2>nul

echo Setup completed! Run: run.bat
pause
