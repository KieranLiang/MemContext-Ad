# 🚀 MemContext-Ad 部署指南

本项目支持多种云平台部署，推荐使用 **Zeabur** 或 **Railway**。

## 📋 部署前准备

### 1. 准备 OpenAI API Key
- 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
- 创建一个新的 API Key
- 或使用兼容的 API 提供商（如 DeepSeek, Azure OpenAI 等）

### 2. 环境变量配置
创建 `.env` 文件（参考项目根目录的环境变量示例）：

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
FLASK_ENV=production
```

---

## 🎯 方案一：Zeabur 部署（最推荐）

### 为什么选择 Zeabur？
- ✅ 完美支持 Docker 和 Python ML 应用
- ✅ 免费额度：5 美元/月（足够小型应用使用）
- ✅ 自动 HTTPS 和域名
- ✅ 支持持久化存储
- ✅ 部署速度快，配置简单

### 部署步骤

#### 1. 注册 Zeabur
访问 [Zeabur.com](https://zeabur.com) 并使用 GitHub 账号登录

#### 2. 连接 GitHub 仓库
```bash
# 1. 将代码推送到 GitHub
git init
git add .
git commit -m "Initial commit for deployment"
git remote add origin https://github.com/your-username/memcontext-ad.git
git push -u origin main
```

#### 3. 在 Zeabur 创建项目
1. 点击 "Create New Project"
2. 选择 "Deploy from GitHub"
3. 授权并选择你的仓库
4. Zeabur 会自动检测到 `Dockerfile` 并开始构建

#### 4. 配置环境变量
在 Zeabur 项目设置中添加以下环境变量：
```
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
FLASK_ENV=production
```

#### 5. 等待部署完成
- 首次构建大约需要 5-10 分钟（下载 ML 模型）
- 部署成功后会分配一个公开域名，如 `https://your-app.zeabur.app`

#### 6. 访问应用
直接访问 Zeabur 提供的域名即可！

---

## 🚂 方案二：Railway 部署

### 为什么选择 Railway？
- ✅ $5/月免费额度（约 500 小时运行时间）
- ✅ 配置简单，界面友好
- ✅ 自动生成域名和 HTTPS
- ✅ 支持 PostgreSQL、Redis 等数据库

### 部署步骤

#### 1. 注册 Railway
访问 [Railway.app](https://railway.app) 并使用 GitHub 登录

#### 2. 创建新项目
```bash
# 安装 Railway CLI（可选）
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init
```

#### 3. 通过 GitHub 部署
1. 在 Railway Dashboard 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择你的仓库
4. Railway 会自动检测 `Dockerfile` 和 `railway.toml`

#### 4. 配置环境变量
在 Railway 项目的 "Variables" 标签添加：
```
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
FLASK_ENV=production
```

#### 5. 添加持久化卷（可选）
```bash
# 如果需要持久化用户数据
railway volume add --mount /app/memdemo/data
railway volume add --mount /app/files
```

#### 6. 部署完成
访问 Railway 提供的域名，如 `https://your-app.railway.app`

---

## 🎨 方案三：Render 部署（备选）

### 特点
- ✅ 永久免费层（但有限制：512MB RAM，睡眠机制）
- ⚠️ 免费层会在 15 分钟无活动后休眠
- ⚠️ ML 模型可能超出内存限制（需要 Starter 计划 $7/月）

### 部署步骤

1. 访问 [Render.com](https://render.com) 注册
2. 连接 GitHub 仓库
3. 选择 "New Web Service"
4. 使用 Docker 环境部署
5. 配置环境变量（同上）
6. 选择计划：
   - **Free**：适合测试，会自动休眠
   - **Starter ($7/月)**：推荐，无休眠，1GB RAM

---

## ⚡ 方案四：Vercel 部署（不推荐）

### 为什么不推荐？
- ❌ Serverless 函数 50MB 大小限制
- ❌ 你的项目包含大量 ML 库（FAISS、transformers）超过 500MB
- ❌ 10 秒执行超时（SSE 流式响应会断开）
- ❌ 不适合有状态应用

如果非要使用 Vercel，需要：
1. 将后端部署到其他平台（Railway/Render）
2. 仅在 Vercel 部署前端静态文件
3. 配置前端 API 请求指向后端服务器

---

## 🔧 部署后优化建议

### 1. 优化 Docker 镜像大小
```dockerfile
# 使用 slim 基础镜像
FROM python:3.10-slim

# 使用多阶段构建
# 第一阶段：构建前端
# 第二阶段：Python 运行时
```

### 2. 减少内存占用
```python
# 在 memdemo/app.py 中配置较小的嵌入模型
# 例如使用 all-MiniLM-L6-v2 代替 bge-m3
```

### 3. 添加日志监控
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 4. 配置 CDN
- Zeabur/Railway 自动提供 CDN
- 可以额外使用 Cloudflare 加速

### 5. 数据持久化
```bash
# Zeabur: 在控制台添加 Volume
# Railway: railway volume add
```

---

## 📊 费用对比

| 平台 | 免费额度 | 适合场景 | 月费用（付费） |
|------|---------|---------|--------------|
| **Zeabur** | $5/月流量 | 🏆 小型-中型项目 | $10/月起 |
| **Railway** | $5/月运行时 | 🏆 中型项目 | $20/月起 |
| **Render** | 永久免费（限制多） | 测试、演示 | $7/月起 |
| **Vercel** | 慷慨免费层 | ❌ 不适合此项目 | $20/月起 |

---

## 🐛 常见问题

### 1. 部署时内存不足？
**解决方案：**
- 使用更小的嵌入模型
- 升级到付费计划（至少 1GB RAM）
- 减少 gunicorn workers 数量

### 2. 应用启动慢？
**原因：** 首次加载 sentence-transformers 模型需要时间
**解决方案：**
- 预下载模型到 Docker 镜像
- 使用模型缓存

### 3. API 请求超时？
**解决方案：**
- 增加 gunicorn timeout：`--timeout 300`
- 使用异步处理长时间任务
- 检查 OpenAI API 响应时间

### 4. 数据丢失？
**解决方案：**
- 配置持久化卷（Volume）
- 使用外部数据库（PostgreSQL、MongoDB）

---

## 📞 获取帮助

- **Zeabur 文档**: https://zeabur.com/docs
- **Railway 文档**: https://docs.railway.app
- **Render 文档**: https://render.com/docs
- **项目 Issues**: 在 GitHub 仓库提交问题

---

## ✅ 部署检查清单

- [ ] 代码已推送到 GitHub
- [ ] 已准备好 OpenAI API Key
- [ ] 已选择云平台（推荐 Zeabur/Railway）
- [ ] 已配置环境变量
- [ ] 已测试健康检查端点 `/api/health`
- [ ] 已配置持久化存储（如需要）
- [ ] 已测试前端访问
- [ ] 已测试聊天功能
- [ ] 已测试文件上传功能

祝部署顺利！🎉

