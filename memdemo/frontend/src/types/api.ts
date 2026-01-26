// API 类型定义
export interface InitMemoryRequest {
  user_id: string;
}

export interface InitMemoryResponse {
  success: boolean;
  session_id?: string;
  user_id?: string;
  assistant_id?: string;
  model?: string;
  base_url?: string;
  embedding_provider?: string;
  error?: string;
}

export interface ChatRequest {
  message: string;
  interest_tag?: string[];
  user_id?: string;
}

export interface ChatResponse {
  response?: string;
  error?: string;
  advertise?: any[];
}

export interface MemoryStateResponse {
  short_term: {
    current_count: number;
    capacity: number;
    memories: Array<{
      user_input: string;
      agent_response: string;
      timestamp: string;
    }>;
  };
  mid_term: {
    current_count: number;
    capacity: number;
    heat_threshold: number;
    sessions: Array<{
      summary: string;
      keywords: string[];
      heat: number;
      visit_count: number;
      page_count: number;
      last_visit: string;
    }>;
  };
  long_term: {
    user_profile: string;
    user_knowledge: string[];
    assistant_knowledge: string[];
  };
  error?: string;
}

export interface ImportConversationsRequest {
  conversations: Array<{
    user_input: string;
    agent_response: string;
    timestamp?: string;
  }>;
}

export interface ImportConversationsResponse {
  success: boolean;
  imported_count?: number;
  error?: string;
}

export interface PersonalityAnalysisResponse {
  success: boolean;
  personality_analysis?: {
    'Psychological Model': Array<{
      dimension: string;
      level: string;
    }>;
    'Content Platform Interest Tags': Array<{
      dimension: string;
      level: string;
    }>;
    'AI Alignment Dimensions': Array<{
      dimension: string;
      level: string;
    }>;
  };
  error?: string;
}
