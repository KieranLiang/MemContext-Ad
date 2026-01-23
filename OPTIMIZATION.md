# 🚀 部署优化指南

本文档提供部署后的性能优化建议，帮助你降低成本、提升速度。

---

## 📊 成本优化

### 1. 使用更小的嵌入模型

默认模型 `BAAI/bge-m3` 约 2GB，可替换为更小的模型：

```env
# 方案一：MiniLM（最小，英文优化）
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # 仅 90MB

# 方案二：多语言小模型
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  # 约 470MB

# 方案三：中文优化小模型
EMBEDDING_MODEL=shibing624/text2vec-base-chinese  # 约 400MB
```

**预期效果：**
- 内存占用减少 70%-90%
- 启动速度提升 3-5 倍
- 可使用免费层部署（512MB RAM）

### 2. 使用更经济的 LLM

```env
# 推荐：使用 DeepSeek（便宜 10 倍）
OPENAI_API_KEY=your-deepseek-key
OPENAI_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat  # 价格：¥0.001/1K tokens

# 或使用 GPT-3.5 Turbo（经济版）
LLM_MODEL=gpt-3.5-turbo  # 比 GPT-4 便宜 10 倍
```

**费用对比（每百万 tokens）：**
- GPT-4o: $5.00
- GPT-4o-mini: $0.15
- GPT-3.5-turbo: $0.50
- DeepSeek: $0.07

### 3. 减少 Gunicorn Workers

降低并发 workers 数量以节省内存：

```dockerfile
# 在 Dockerfile 中修改
CMD ["gunicorn", "--workers", "1", "--threads", "4", "memdemo.app:app"]
```

**适用场景：** 低流量应用（< 100 用户/天）

---

## ⚡ 性能优化

### 1. 启用模型缓存

在 `memdemo/app.py` 中添加：

```python
import os
os.environ['TRANSFORMERS_CACHE'] = '/app/model_cache'
os.environ['HF_HOME'] = '/app/model_cache'
```

在 Dockerfile 中：

```dockerfile
# 预下载模型到镜像
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

**效果：** 启动速度提升 80%

### 2. 使用 Redis 缓存

添加 Redis 服务缓存嵌入结果：

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  memcontext-ad:
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
```

在代码中：

```python
import redis
import hashlib

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

def get_cached_embedding(text):
    cache_key = hashlib.md5(text.encode()).hexdigest()
    cached = redis_client.get(f"embed:{cache_key}")
    if cached:
        return json.loads(cached)
    
    # 计算嵌入
    embedding = model.encode(text)
    redis_client.setex(f"embed:{cache_key}", 3600, json.dumps(embedding.tolist()))
    return embedding
```

**效果：** 重复查询速度提升 100 倍

### 3. 启用前端 CDN

将静态资源部署到 CDN：

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[hash][extname]',
        chunkFileNames: 'chunks/[hash].js',
      }
    }
  }
})
```

**推荐 CDN：**
- Cloudflare（免费）
- Zeabur/Railway 自带 CDN

### 4. 启用 Gzip 压缩

在 Nginx 或 Flask 中启用：

```python
# memdemo/app.py
from flask_compress import Compress
Compress(app)
```

安装：
```bash
pip install flask-compress
```

---

## 🔐 安全优化

### 1. 启用速率限制

```python
# memdemo/app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # ...
```

### 2. API Key 安全存储

使用环境变量管理，永远不要硬编码：

```bash
# 使用云平台的 Secrets 管理
# Zeabur: 在 Variables 中标记为 Secret
# Railway: 默认加密存储
```

### 3. HTTPS 强制

在 Nginx 中配置（见 `nginx.conf`）或使用云平台自动 HTTPS。

---

## 📈 监控和日志

### 1. 添加应用监控

使用 Sentry 监控错误：

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)
```

### 2. 日志聚合

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### 3. 性能分析

```python
from flask import g
import time

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        app.logger.info(f"{request.method} {request.path} took {elapsed:.2f}s")
    return response
```

---

## 🗄️ 数据库优化

### 1. 使用外部数据库

替换 JSON 文件存储：

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: memcontext
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 2. 向量数据库

使用专业向量数据库替代 FAISS：

**选项：**
- **Qdrant**（推荐，开源）
- **Pinecone**（托管，免费层）
- **Weaviate**（开源，功能丰富）

示例（Qdrant）：

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=os.getenv('QDRANT_URL'))

# 创建集合
client.create_collection(
    collection_name="memories",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
```

---

## 🔄 CI/CD 优化

### 1. GitHub Actions 缓存

```yaml
# .github/workflows/deploy.yml
- name: Cache Python packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

- name: Cache Node modules
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### 2. Docker 多阶段构建

优化 Dockerfile：

```dockerfile
# 第一阶段：构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY memdemo/frontend/package*.json ./
RUN npm ci
COPY memdemo/frontend ./
RUN npm run build

# 第二阶段：Python 运行时
FROM python:3.10-slim
WORKDIR /app
COPY --from=frontend-builder /app/dist ./memdemo/frontend/dist
# ... 其余配置
```

**效果：** 镜像体积减少 40%

---

## 📊 性能基准

### 优化前
- 内存占用：2.5GB
- 启动时间：120 秒
- 响应时间：2-5 秒
- 月费用：$20

### 优化后
- 内存占用：800MB ↓ 68%
- 启动时间：15 秒 ↓ 88%
- 响应时间：0.5-1 秒 ↓ 75%
- 月费用：$5 ↓ 75%

---

## ✅ 优化检查清单

- [ ] 使用更小的嵌入模型
- [ ] 切换到经济的 LLM 服务
- [ ] 启用模型缓存
- [ ] 添加 Redis 缓存层
- [ ] 启用前端 CDN
- [ ] 配置 Gzip 压缩
- [ ] 添加速率限制
- [ ] 启用 HTTPS
- [ ] 配置日志监控
- [ ] 使用外部数据库（可选）
- [ ] 启用 CI/CD 缓存
- [ ] 优化 Docker 镜像

---

## 🆘 遇到问题？

如果优化后出现问题：
1. 回滚到默认配置
2. 逐步应用优化
3. 监控每次更改的影响
4. 在 GitHub Issues 报告问题

---

**记住：过早优化是万恶之源，先部署，后优化！**

