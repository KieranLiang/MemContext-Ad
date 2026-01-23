import { useState, useCallback, useRef } from 'react';
import { chatStream } from '../services/api';
import type { ChatRequest } from '../types/api';

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 使用 ref 来追踪完成状态，避免多次调用重置
  const isCompletedRef = useRef(false);

  const sendMessage = useCallback(
    async (
      data: ChatRequest,
      onChunk: (chunk: string) => void,
      onAdvertise?: (ads: any[]) => void
    ) => {
      // 如果正在流式传输，则忽略
      if (isStreaming) return;

      setIsStreaming(true);
      setError(null);
      isCompletedRef.current = false;

      const resetStreaming = () => {
        if (!isCompletedRef.current) {
          isCompletedRef.current = true;
          setIsStreaming(false);
        }
      };

      try {
        await chatStream(
          data,
          (chunk) => {
            onChunk(chunk);
          },
          (ads) => {
            onAdvertise?.(ads);
          },
          () => {
            resetStreaming();
          },
          (err) => {
            setError(err);
            resetStreaming();
          },
          () => {
            // 当文字输出结束时，立即解锁输入框
            // 但不标记 isCompletedRef = true，因为后续还有广告数据要接收
            setIsStreaming(false);
          }
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        // 兜底保障：无论发生什么，最后都重置状态
        resetStreaming();
      }
    },
    [isStreaming]
  );

  return {
    sendMessage,
    isStreaming,
    error,
  };
}
