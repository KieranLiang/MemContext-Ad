# 🚀 MemContext-Ad 快速部署指南

> 选择最适合你的部署方式，5 分钟上线！

---

## 📋 部署前准备清单

- [ ] 已有 OpenAI API Key（或兼容服务）
- [ ] 代码已推送到 GitHub（云部署需要）
- [ ] 已阅读 `ENV_VARIABLES.md` 了解环境变量

---

## 🎯 方式一：Zeabur 一键部署（推荐）

**适合人群**: 希望快速部署，无需配置服务器

### 步骤

#### 1. 点击一键部署按钮

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com/templates)

#### 2. 或者手动部署

1. 访问 [Zeabur.com](https://zeabur.com) 并登录
2. 点击 "Create New Project"
3. 选择 "Deploy from GitHub"
4. 选择本仓库 `MemContext-Ad`
5. 配置环境变量：
   ```
   OPENAI_API_KEY=your-api-key
   OPENAI_API_BASE=https://api.openai.com/v1
   LLM_MODEL=gpt-4o-mini
   FLASK_ENV=production
   ```
6. 点击 "Deploy"，等待 5-10 分钟
7. 访问 Zeabur 分配的域名 ✅

### 费用
- **免费额度**: $5/月
- **付费计划**: $10/月起

---

## 🚂 方式二：Railway 快速部署

**适合人群**: 需要可靠的云平台，预算充足

### 步骤

#### 1. 点击一键部署

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

#### 2. 或者手动部署

1. 访问 [Railway.app](https://railway.app) 并登录
2. 创建 "New Project" → "Deploy from GitHub repo"
3. 选择本仓库
4. Railway 自动检测 `Dockerfile`
5. 配置环境变量（同 Zeabur）
6. 等待构建完成
7. 访问分配的域名 ✅

### 费用
- **免费额度**: $5/月（约 500 小时）
- **付费计划**: $20/月起

---

## 🐳 方式三：Docker 本地部署

**适合人群**: 有自己的服务器，或希望完全控制

### 使用 Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/memcontext-ad.git
cd memcontext-ad

# 2. 创建 .env 文件
cp ENV_VARIABLES.md .env
# 编辑 .env 填入你的 API Key

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问应用
# http://localhost:5019
```

### 使用 Dockerfile

```bash
# 1. 构建镜像
docker build -t memcontext-ad .

# 2. 运行容器
docker run -d \
  -p 5019:5019 \
  -e OPENAI_API_KEY=your-key \
  -e OPENAI_API_BASE=https://api.openai.com/v1 \
  -e LLM_MODEL=gpt-4o-mini \
  -e FLASK_ENV=production \
  -v $(pwd)/memdemo/data:/app/memdemo/data \
  -v $(pwd)/files:/app/files \
  --name memcontext-ad \
  memcontext-ad

# 3. 查看日志
docker logs -f memcontext-ad
```

---

## 💻 方式四：本地开发模式

**适合人群**: 开发者，需要修改代码

### Windows

```bash
# 双击运行
start.bat

# 或者手动启动
cd memdemo\frontend
npm install
npm run dev

# 新开终端
cd memdemo
pip install -r requirements.txt
python app.py
```

### Linux/Mac

```bash
# 使用启动脚本
chmod +x start.sh
./start.sh

# 或者手动启动（同上）
```

---

## 🔍 验证部署

部署成功后，访问以下端点检查：

### 健康检查
```bash
curl https://your-domain.com/api/health
```

应返回：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-23T12:00:00",
  "service": "memcontext-ad"
}
```

### 前端访问
在浏览器打开 `https://your-domain.com`，应该看到登录页面。

---

## 🛠️ 常见问题

### 1. 部署后显示 502/504 错误？
**原因**: 应用启动需要时间（加载 ML 模型）
**解决**: 等待 2-3 分钟，然后刷新页面

### 2. API 请求失败？
**检查**:
- 环境变量 `OPENAI_API_KEY` 是否正确？
- API Key 是否有余额？
- `OPENAI_API_BASE` 格式是否正确？

### 3. 内存不足错误？
**原因**: ML 模型需要至少 1GB 内存
**解决**:
- 升级到付费计划
- 使用更小的嵌入模型（见 `ENV_VARIABLES.md`）

### 4. 文件上传失败？
**原因**: 未配置持久化存储
**解决**:
- Zeabur/Railway: 添加 Volume
- Docker: 挂载卷（已在 `docker-compose.yml` 中配置）

---

## 📊 部署方式对比

| 方式 | 难度 | 速度 | 费用 | 推荐度 |
|------|------|------|------|--------|
| **Zeabur** | ⭐ | ⚡⚡⚡ | $5 免费额度 | ⭐⭐⭐⭐⭐ |
| **Railway** | ⭐ | ⚡⚡⚡ | $5 免费额度 | ⭐⭐⭐⭐⭐ |
| **Docker** | ⭐⭐ | ⚡⚡ | 服务器费用 | ⭐⭐⭐⭐ |
| **本地** | ⭐⭐⭐ | ⚡ | 免费 | ⭐⭐⭐ |

---

## 🎉 下一步

部署成功后，你可以：

1. 📝 阅读 `README.md` 了解功能
2. 🧪 测试聊天和记忆功能
3. 📊 查看广告推荐系统
4. 🔧 自定义提示词（`memcontext/prompts.py`）
5. 📈 监控应用性能

---

## 📞 需要帮助？

- 📖 完整部署文档: `DEPLOYMENT.md`
- 🔐 环境变量配置: `ENV_VARIABLES.md`
- 🐛 报告问题: [GitHub Issues](https://github.com/your-username/memcontext-ad/issues)

---

**祝部署顺利！🚀**

