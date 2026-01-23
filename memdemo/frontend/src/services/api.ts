import axios from 'axios';
import type {
  InitMemoryRequest,
  InitMemoryResponse,
  ChatRequest,
  ChatResponse,
  MemoryStateResponse,
  ImportConversationsRequest,
  ImportConversationsResponse,
  PersonalityAnalysisResponse,
} from '../types/api';

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '', // Vite 代理会处理 /api
  timeout: 60000,
  withCredentials: true, // 重要：保持会话 Cookie
});

// 请求拦截器
api.interceptors.request.use((config) => {
  console.log(`请求 ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 错误:', error);
    return Promise.reject(error);
  },
);

// 记忆系统初始化
export const initMemory = async (data: InitMemoryRequest): Promise<InitMemoryResponse> => {
  const response = await api.post('/api/init_memory', data);
  return response.data;
};

// 聊天接口（SSE 流式传输）
export const chatStream = async (
  data: ChatRequest,
  onMessage: (chunk: string) => void,
  onAdvertise?: (ads: any[]) => void,
  onDone?: () => void,
  onError?: (error: string) => void,
  onTextDone?: () => void
) => {
  let reader: ReadableStreamDefaultReader<Uint8Array> | undefined;
  
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, ${errorText}`);
    }

    reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    let buffer = '';
    let streamDone = false;

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim() === '') continue;
        
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6).trim();
            if (!jsonStr || jsonStr === '[DONE]') {
              streamDone = true;
              return; // 直接返回，触发 finally
            }

            const parsedData = JSON.parse(jsonStr);

            if (parsedData.response) {
              onMessage(parsedData.response);
            }
            if (parsedData.text_done) {
              onTextDone?.();
            }
            if (parsedData.advertise) {
              onAdvertise?.(parsedData.advertise);
            }
            if (parsedData.done) {
              streamDone = true;
              return; // 直接返回，触发 finally
            }
            if (parsedData.error) {
              throw new Error(parsedData.error);
            }
          } catch (e) {
            console.error('Parse SSE data error:', e, line);
            if (e instanceof Error && e.message !== 'Parse SSE data error') {
                // 如果是 error 消息抛出的错误，再抛出去
                throw e; 
            }
          }
        }
      }
    }
  } catch (error) {
    onError?.(error instanceof Error ? error.message : 'Unknown error');
  } finally {
    if (reader) {
      try {
        await reader.cancel();
      } catch (e) {
        console.error('Error cancelling reader:', e);
      }
    }
    // 无论如何都通知结束
    onDone?.();
  }
};

// 获取记忆状态
export const getMemoryState = async (): Promise<MemoryStateResponse> => {
  const response = await api.get('/api/memory_state');
  return response.data;
};

// 触发分析
export const triggerAnalysis = async (): Promise<{ success: boolean; error?: string }> => {
  const response = await api.post('/api/trigger_analysis');
  return response.data;
};

// 性格分析
export const getPersonalityAnalysis = async (): Promise<PersonalityAnalysisResponse> => {
  const response = await api.post('/api/personality_analysis');
  return response.data;
};

// 清空记忆
export const clearMemory = async (): Promise<{ success: boolean; error?: string }> => {
  const response = await api.post('/api/clear_memory');
  return response.data;
};

// 广告推荐接口
export const getAdvertising = async (data: AdvertisingRequest): Promise<AdvertisingResponse> => {
  const response = await api.post('/advertise', data);
  return response.data;
};

// 导入对话
export const importConversations = async (
  data: ImportConversationsRequest,
): Promise<ImportConversationsResponse> => {
  const response = await api.post('/api/import_conversations', data);
  return response.data;
};

// 其他接口...

export default api;
