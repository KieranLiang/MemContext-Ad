# MemContext-Ad
Affiliate Marketing Platform For AI Agents with Long-term Memory and Multimodal capabilities.

## 🚀 快速部署

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

**5 分钟部署指南**: [QUICKSTART.md](QUICKSTART.md) ⚡

**完整部署文档**: [DEPLOYMENT.md](DEPLOYMENT.md) 📚

## 项目结构 (Project Structure)

- **Backend (`memdemo/`)**: Flask-based API server handling memory logic, LLM interaction, and RAG.
- **Frontend (`memdemo/frontend/`)**: Modern React + TypeScript application (Vite) providing the Gemini-like chat interface.
- **Core Library (`memcontext/`)**: The core memory management system.

## 🚀 快速启动指南 (Quick Start)

本项目分为后端 (Flask) 和前端 (React) 两部分，需要分别启动。

### 1. 启动后端 (Backend)

确保你已安装 Python 3.10+。

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量
# 复制 .env.default 为 .env 并填入你的 API Key
cp .env.default .memdemo/.env
# 编辑 .memdemo/.env 文件...

# 3. 启动 Flask 服务器
python memdemo/app.py
```
*后端服务器默认运行在 http://localhost:5019*

### 2. 启动前端 (Frontend)

确保你已安装 Node.js (推荐 v18+)。

```bash
# 1. 进入前端目录
cd memdemo/frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

*前端开发服务器默认运行在 http://localhost:5173*

## 访问应用

打开浏览器访问前端地址：**http://localhost:5173**

前端 (Vite) 会自动将 `/api` 请求代理到后端 (Flask :5019)，无需额外配置跨域。

## 🚀 生产部署 (Production Deployment)

### 快速部署到云平台

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

**详细部署指南**: 
- 📖 [快速开始](QUICKSTART.md) - 5 分钟部署指南
- 📚 [完整文档](DEPLOYMENT.md) - 详细配置说明
- 🔐 [环境变量](ENV_VARIABLES.md) - API Key 配置

### 本地构建生产版本

```bash
# 1. 构建前端
cd memdemo/frontend
npm run build

# 2. 启动生产服务器
cd ../..
export FLASK_ENV=production
python memdemo/app.py
```

### Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 或使用 Dockerfile
docker build -t memcontext-ad .
docker run -p 5019:5019 memcontext-ad
```
