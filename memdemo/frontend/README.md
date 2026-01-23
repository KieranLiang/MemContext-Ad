# MemContext Frontend (React)

React + TypeScript 前端应用，保持 Gemini 风格设计。

## 快速开始

### 安装依赖
```bash
cd memdemo/frontend
npm install
```

### 开发模式
```bash
npm run dev
```

前端将在 `http://localhost:5173` 运行，Vite 会自动代理 `/api` 请求到 Flask 后端 (`http://localhost:5000`)

### 构建生产版本
```bash
npm run build
```

## 项目结构

```
src/
├── components/     # 组件
│   ├── FloatingNav.tsx
│   ├── ChatWelcome.tsx
│   ├── ChatMessage.tsx
│   └── ChatInput.tsx
├── pages/         # 页面
│   ├── LoginPage.tsx
│   ├── ChatPage.tsx
│   └── MemoryPage.tsx
├── hooks/         # Hooks
│   └── useSSE.ts
├── services/      # API 服务
│   └── api.ts
└── types/         # 类型定义
    └── api.ts
```

## 功能

- ✅ 登录页面（Gemini 风格）
- ✅ 聊天页面（SSE 流式传输）
- ✅ 记忆管理页面
- ✅ 左侧悬浮导航
- ✅ 响应式设计

## 技术栈

- React 19
- TypeScript
- Vite
- React Router
- Axios
- Marked (Markdown 渲染)
