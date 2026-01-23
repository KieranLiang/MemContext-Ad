#!/bin/bash

# MemContext-Ad 一键启动脚本
# 用于本地开发和测试

set -e  # 遇到错误立即退出

echo "🚀 Starting MemContext-Ad..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 .env 文件
if [ ! -f "memdemo/.env" ] && [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please create .env file with your API keys."
    echo "You can copy from ENV_VARIABLES.md for reference."
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 not found!${NC}"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# 安装 Python 依赖
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1
pip install -r memdemo/requirements.txt > /dev/null 2>&1

# 安装前端依赖
if [ ! -d "memdemo/frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd memdemo/frontend
    npm install > /dev/null 2>&1
    cd ../..
fi

# 启动后端
echo -e "${GREEN}🔧 Starting Flask backend...${NC}"
cd memdemo
python app.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo -e "${GREEN}🎨 Starting React frontend...${NC}"
cd memdemo/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo -e "${GREEN}✅ MemContext-Ad is running!${NC}"
echo ""
echo "📍 Backend:  http://localhost:5019"
echo "📍 Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# 捕获 Ctrl+C 信号
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# 保持脚本运行
wait

