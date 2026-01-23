# MemContext-Ad
Affiliate Marketing Platform For AI Agents with Long-term Memory and Multimodal capabilities.

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

## 生产构建 (Build for Production)

如果你想部署生产版本：

1.  在前端目录运行 `npm run build` 生成静态文件。
2.  将生成的 `dist/` 目录内容部署到 Web 服务器，或配置 Flask 托管静态文件。
