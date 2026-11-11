@echo off
echo CLEVER AI - Ollama Setup
echo ========================
echo.

echo Step 1: Checking for Ollama installation...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Ollama not found! Please install from: https://ollama.ai
    echo.
    echo Press any key to open download page...
    pause >nul
    start https://ollama.ai/download
    exit /b
)

echo ✅ Ollama found!

echo.
echo Step 2: Pulling Llama2 model (this may take a while)...
ollama pull llama2

echo.
echo Step 3: Testing Ollama...
echo "Hello" | ollama run llama2

echo.
echo ✅ Ollama setup complete!
echo.
echo You can now run CLEVER with Ollama mode enabled.
pause