# 🔐 环境变量配置指南

## 必需环境变量

复制以下内容创建 `.env` 文件：

```env
# ============================================
# OpenAI API 配置（必需）
# ============================================
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# ============================================
# Flask 应用配置
# ============================================
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here

# ============================================
# 文件上传配置（可选）
# ============================================
MAX_CONTENT_LENGTH=104857600
UPLOAD_FOLDER=./files
```

---

## 详细说明

### 1. OPENAI_API_KEY
- **必需**: ✅ 是
- **说明**: OpenAI API 密钥
- **获取方式**: 
  - 访问 https://platform.openai.com/api-keys
  - 点击 "Create new secret key"
- **格式**: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**替代方案（兼容 OpenAI API 的服务）：**
```env
# 使用 DeepSeek API
OPENAI_API_KEY=your-deepseek-api-key
OPENAI_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# 使用 Azure OpenAI
OPENAI_API_KEY=your-azure-api-key
OPENAI_API_BASE=https://your-resource.openai.azure.com/
LLM_MODEL=gpt-4

# 使用阿里云通义千问
OPENAI_API_KEY=your-dashscope-api-key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

### 2. OPENAI_API_BASE
- **必需**: ✅ 是
- **说明**: API 端点地址
- **默认值**: `https://api.openai.com/v1`
- **注意**: 末尾不要加 `/`

### 3. LLM_MODEL
- **必需**: ✅ 是
- **说明**: 使用的语言模型
- **推荐选项**:
  - `gpt-4o-mini` - 最新高效模型（推荐）
  - `gpt-4o` - 更强大但更贵
  - `gpt-3.5-turbo` - 经济实惠
  - `gpt-4-turbo` - 高性能

### 4. FLASK_ENV
- **必需**: ⚠️ 生产环境必需
- **说明**: Flask 运行模式
- **选项**:
  - `production` - 生产模式（部署时使用）
  - `development` - 开发模式（本地使用）

### 5. SECRET_KEY
- **必需**: ⚠️ 生产环境推荐
- **说明**: Flask session 加密密钥
- **生成方式**:
```bash
# Python 生成
python -c "import secrets; print(secrets.token_hex(32))"

# 或
openssl rand -hex 32
```

### 6. MAX_CONTENT_LENGTH
- **必需**: ❌ 否
- **说明**: 最大上传文件大小（字节）
- **默认值**: `104857600`（100MB）

### 7. UPLOAD_FOLDER
- **必需**: ❌ 否
- **说明**: 文件上传目录
- **默认值**: `./files`

---

## 嵌入模型配置（可选）

如果需要自定义嵌入模型：

```env
# 使用 BGE-M3（更好的中文支持，但更大）
EMBEDDING_MODEL=BAAI/bge-m3

# 使用 MiniLM（更小更快）
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# 使用 Qwen（中文优化）
EMBEDDING_MODEL=Qwen/Qwen2-0.5B-Instruct
```

---

## 云平台配置示例

### Zeabur
在 Zeabur Dashboard → Variables 中添加：
```
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
FLASK_ENV=production
```

### Railway
在 Railway Dashboard → Variables 中添加（同上）

### Render
在 Render Dashboard → Environment 中添加（同上）

---

## 安全建议

1. **永远不要**将 `.env` 文件提交到 Git
2. 已添加到 `.gitignore`：
   ```gitignore
   .env
   .env.local
   .env.*.local
   ```

3. 定期轮换 API Keys

4. 使用环境变量管理工具：
   - 云平台自带的环境变量管理
   - 本地开发使用 `.env` 文件
   - CI/CD 使用加密的 secrets

5. 限制 API Key 权限（如果平台支持）

---

## 验证配置

部署后访问健康检查端点：
```bash
curl https://your-app.zeabur.app/api/health
```

应返回：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-23T12:00:00",
  "service": "memcontext-ad"
}
```

---

## 故障排查

### 问题：API 请求失败
**检查：**
- OPENAI_API_KEY 是否正确？
- OPENAI_API_BASE 格式是否正确？
- API Key 是否有余额？

### 问题：模型加载失败
**检查：**
- 内存是否足够（至少 1GB）？
- 嵌入模型是否可访问？

### 问题：文件上传失败
**检查：**
- MAX_CONTENT_LENGTH 是否足够大？
- 磁盘空间是否充足？
- 是否配置了持久化卷？

---

## 更多帮助

参考 `DEPLOYMENT.md` 获取完整部署指南。

