# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（faiss 和 transformers 需要）
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY memdemo/requirements.txt memdemo/requirements.txt

# 安装 Python 依赖（使用 CPU 版本的 faiss）
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r memdemo/requirements.txt && \
    pip install gunicorn

# 复制项目文件
COPY . .

# 安装 Node.js 22 用于构建前端
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# 构建前端
WORKDIR /app/memdemo/frontend
RUN npm install && npm run build

# 回到主工作目录
WORKDIR /app

# 创建必要的目录
RUN mkdir -p memdemo/data/users memdemo/data/assistants files/images files/videos files/audio files/documents files/metadata

# 暴露端口
EXPOSE 5019

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5019", "--workers", "2", "--threads", "4", "--timeout", "300", "memdemo.app:app"]

