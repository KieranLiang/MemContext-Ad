@echo off
REM MemContext-Ad 一键启动脚本 (Windows)
REM 用于本地开发和测试

echo Starting MemContext-Ad...

REM 检查 .env 文件
if not exist "memdemo\.env" if not exist ".env" (
    echo Error: .env file not found!
    echo Please create .env file with your API keys.
    echo You can copy from ENV_VARIABLES.md for reference.
    pause
    exit /b 1
)

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found!
    pause
    exit /b 1
)

REM 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Node.js not found!
    pause
    exit /b 1
)

echo Prerequisites check passed

REM 安装 Python 依赖
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
pip install -r memdemo\requirements.txt >nul 2>&1

REM 安装前端依赖
if not exist "memdemo\frontend\node_modules" (
    echo Installing frontend dependencies...
    cd memdemo\frontend
    call npm install >nul 2>&1
    cd ..\..
)

REM 启动后端
echo Starting Flask backend...
start "MemContext Backend" cmd /k "cd memdemo && python app.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo Starting React frontend...
start "MemContext Frontend" cmd /k "cd memdemo\frontend && npm run dev"

echo.
echo MemContext-Ad is running!
echo.
echo Backend:  http://localhost:5019
echo Frontend: http://localhost:5173
echo.
echo Close the command windows to stop the services.
pause

