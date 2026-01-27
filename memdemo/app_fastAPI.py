# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from concurrent.futures import ThreadPoolExecutor
import asyncio
from typing import Optional, Dict, Any, List
import sys
import os
import json
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
import secrets
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add parent directory to path to import memcontext
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import memcontext modules directly
from memcontext import Memcontext
from memcontext.utils import get_timestamp

# 创建 FastAPI 应用
app = FastAPI(title="MemContext API Server")

# CORS 配置 - 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 线程池用于执行同步操作
executor = ThreadPoolExecutor(max_workers=10)

# Global memcontext instance (in production, you'd use proper session management)
memory_systems: Dict[str, Memcontext] = {}
# Session storage: session_id -> user_id mapping
session_storage: Dict[str, Dict[str, Any]] = {}

# 商品数据(用于广告推荐)
ad_data_dir = os.path.join(os.path.dirname(__file__), 'ad_data')
with open(os.path.join(ad_data_dir, 'ad_demo_format.json'), 'r', encoding='utf-8') as f: 
    ads_data = json.load(f)
    ads_data = ads_data["advertisements"]
with open(os.path.join(ad_data_dir, 'forbidden_keywords.json'), 'r', encoding='utf-8') as f: 
    forbidden_keywords = json.load(f)
    forbidden_keywords = forbidden_keywords.get("forbidden_words", forbidden_keywords.get("forbidden_keywords", []))

with open(os.path.join(ad_data_dir, 'all_tags.json'), 'r', encoding='utf-8') as f:
    all_tags_data = json.load(f)
    available_tags = all_tags_data.get("tags", [])

interest_log = {}

# 依赖注入：从请求头或 cookie 获取 session_id
async def get_session_id(request: Request) -> Optional[str]:
    """从请求头或 cookie 获取 session_id"""
    # 优先从 header 获取
    session_id = request.headers.get('X-Session-ID')
    if not session_id:
        # 从 cookie 获取
        session_id = request.cookies.get('session_id')
    return session_id

# 依赖注入：获取 memory_system
async def get_memory_system(session_id: Optional[str] = Depends(get_session_id)) -> Memcontext:
    """获取 memory_system，如果不存在则抛出异常"""
    if not session_id or session_id not in memory_systems:
        raise HTTPException(status_code=400, detail='Memory system not initialized')
    return memory_systems[session_id]

@app.get('/')
async def index():
    return "MemContext API Server is running. Please access the frontend via the Vite development server or the built static files."

# Pydantic models for request/response
from pydantic import BaseModel

class InitMemoryRequest(BaseModel):
    user_id: str
    file_storage_base_path: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    user_id: str

class ImportCacheRequest(BaseModel):
    file_id: str

class AddMultimodalMemoryRequest(BaseModel):
    file_path: Optional[str] = None
    url: Optional[str] = None
    converter_type: Optional[str] = None
    agent_response: Optional[str] = None
    converter_kwargs: Optional[Dict[str, Any]] = {}

class ImportConversationsRequest(BaseModel):
    conversations: List[Dict[str, Any]]

@app.post('/init_memory')
async def init_memory(request_data: InitMemoryRequest):
    user_id = request_data.user_id.strip()
    # 豆包配置从环境变量读取
    api_key = os.environ.get('LLM_API_KEY', '').strip()
    base_url = os.environ.get('LLM_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3').strip()
    model = os.environ.get('LLM_MODEL', 'doubao-seed-1-6-flash-250828').strip()
    embedding_model = os.environ.get('EMBEDDING_MODEL', 'doubao-embedding-large-text-250515').strip()

    if not user_id:
        raise HTTPException(status_code=400, detail='User ID 是必需的。')
    
    if not api_key:
        raise HTTPException(status_code=400, detail='LLM_API_KEY 环境变量未配置，请设置豆包 API Key。')
    
    assistant_id = f"assistant_{user_id}"
    
    try:
        # Initialize memcontext for this session
        data_path = './data'
        os.makedirs(data_path, exist_ok=True)
        
        # 获取 file_storage_base_path（可选，默认使用项目根目录）
        file_storage_base_path = request_data.file_storage_base_path
        if not file_storage_base_path or not file_storage_base_path.strip():
            # 默认使用项目根目录
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            file_storage_base_path = project_root
        
        memory_system = Memcontext(
            user_id=user_id,
            openai_api_key=api_key,
            openai_base_url=base_url,
            data_storage_path=data_path,
            assistant_id=assistant_id,
            short_term_capacity=7,
            mid_term_capacity=200,
            long_term_capacity=1000,
            mid_term_heat_threshold=10.0,
            embedding_model_name=embedding_model,
            embedding_model_kwargs={},
            llm_model=model,
            file_storage_base_path=file_storage_base_path
        )
        
        session_id = secrets.token_hex(8)
        memory_systems[session_id] = memory_system
        session_storage[session_id] = {
            'user_id': user_id,
            'memory_config': {
                'api_key': api_key,
                'base_url': base_url,
                'model': model,
                'embedding_provider': 'doubao'
            }
        }
        
        response = JSONResponse({
            'success': True,
            'session_id': session_id,
            'user_id': user_id,
            'assistant_id': assistant_id,
            'model': model,
            'base_url': base_url,
            'embedding_provider': 'doubao'
        })
        # 设置 cookie
        response.set_cookie(key='session_id', value=session_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_user_tags(memory_system):
    """获取用户标签"""
    user_profile = memory_system.user_long_term_memory.get_raw_user_profile(memory_system.user_id)
    if not user_profile or user_profile.lower() in ["null", "none", "no profile data yet"]:
        return {'interests':[], "personality_traits":[]}
    try:
        personality_traits = parse_personality_traits(user_profile)
        interests_tags=personality_traits.get("Content Platform Interest Tags", [])
        user_interests = []
        for interest in interests_tags:
            level = interest.get("level", "").lower()
            dimension = interest.get("dimension", "")
            if level in ["high", "medium"] and dimension:
                interest = dimension.replace("Interest", "").replace("Concern", "").replace("Activity", "").strip()
                if interest:
                    user_interests.append(interest)
        psychological_traits = personality_traits.get("Psychological Model", [])
        user_personality_traits = []
        for trait in psychological_traits:
            level = trait.get("level", "").lower()
            dimension = trait.get("dimension", "")
            if level in ["high", "medium"] and dimension:
                trait = dimension.replace("Need for", "").replace("Need", "").strip()
                if trait:
                    user_personality_traits.append(trait)
        return {'interests':user_interests, "personality_traits":user_personality_traits}
    except Exception as e:
        print(f"DEBUG [Ad]: Error getting user tags: {e}", flush=True)
        return {'interests':[], "personality_traits":[]}

@app.post('/chat')
async def chat(request_data: ChatRequest, memory_system: Memcontext = Depends(get_memory_system)):
    user_input = request_data.message
    user_id = request_data.user_id.strip()

    def advertise(mem_sys, uid, tags, current_input):
        import time
        start_time = time.time()
        print(f"DEBUG [Ad]: advertise task started for user={uid} at {time.strftime('%H:%M:%S')}", flush=True)
        recommended_ads = [] 
        rec_topics = set()
        rec_keywords = set()

        if not tags or not uid:
            print(f"DEBUG [Ad]: Missing tags or uid. Tags={tags}, UID={uid}", flush=True)
            return []
        
        if uid not in interest_log:
            interest_log[uid] = []
        interest_log[uid].append({
            'interest_tag': tags,
            'timestamp': get_timestamp()
        })
        
        short_term_memories = []
        try:
            short_term_memories = mem_sys.short_term_memory.get_all()
            print(f"DEBUG [Ad]: User {uid} short-term memories retrieved: {len(short_term_memories)}", flush=True)
        except Exception as e:
            print(f"DEBUG [Ad]: Error retrieving memories: {e}", flush=True)

        # 构建 Prompt
        tags_library_str = json.dumps(available_tags, ensure_ascii=False)
        user_profile_str = json.dumps(tags, ensure_ascii=False)
        personality_traits = tags.get('personality_traits', [])
        
        prompt = (
            f"你是一个专业的广告匹配引擎的标签选择器。\n"
            f"【候选标签库】：\n{tags_library_str}\n\n"
            f"【用户画像】：\n{user_profile_str}\n\n"
            f"【用户当前输入】：\n{current_input}\n\n"
            f"【用户兴趣标签】：\n{tags}\n\n"
            f"任务：根据用户的输入、对话语境以及用户画像，从【候选标签库】中挑选出最相关的 3-8 个标签用于推荐广告。\n"
            f"\n"
            f"注意：如果用户输入的文本有关健康、心理健康、政治等敏感内容，请不要输出任何标签，并返回一个空列表[]。"
            f"【用户性格特征】：\n{personality_traits}\n\n"
            f"要求：\n"
            f"1. **必须且只能**从【候选标签库】中选择，严禁创造新标签。\n"
            f"2. 返回格式必须是纯 JSON 数组，例如：[\"标签1\", \"标签2\"]。\n"
            f"3. 如果没有相关标签，返回空数组 []。\n"
        )

        try:
            print(f"DEBUG [Ad]: Calling LLM for tag selection...", flush=True)
            from concurrent.futures import TimeoutError as FutureTimeoutError
            llm_future = executor.submit(
                mem_sys.client.chat_completion,
                model=mem_sys.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                stream=False
            )
            try:
                recommendation = llm_future.result(timeout=10)
                print(f"DEBUG [Ad]: LLM Response: {recommendation[:100] if recommendation else '(empty)'}...", flush=True)
            except FutureTimeoutError:
                print(f"DEBUG [Ad]: LLM call timed out after 10 seconds", flush=True)
                recommendation = ""
            
            extracted_tags = []
            if recommendation and recommendation.strip():
                try:
                    clean_json = recommendation
                    if "```" in clean_json:
                        clean_json = re.sub(r"```json\s*|\s*```", "", clean_json, flags=re.IGNORECASE).strip()
                    
                    parsed_data = json.loads(clean_json)
                    if isinstance(parsed_data, list):
                        extracted_tags = parsed_data
                    elif isinstance(parsed_data, dict) and 'tags' in parsed_data:
                        extracted_tags = parsed_data['tags']
                    
                except Exception as e:
                    print(f"DEBUG [Ad]: JSON parsing failed: {e}. Response: {recommendation[:200]}", flush=True)
            else:
                print(f"DEBUG [Ad]: Empty or invalid LLM response, skipping tag extraction", flush=True)

            rec_tags = set(t for t in extracted_tags if t in available_tags)
            
            if not rec_tags:
                print(f"DEBUG [Ad]: No tags from LLM, using fallback keyword matching", flush=True)
                user_input_lower = current_input.lower()
                for tag in available_tags:
                    if tag in user_input_lower or tag in str(tags):
                        rec_tags.add(tag)
                        if len(rec_tags) >= 5:
                            break
            
            print(f"DEBUG [Ad]: AI Selected Valid Tags: {rec_tags}", flush=True)

            for ad in ads_data:
                ad_tags = set(ad.get('tags', []))
                if ad_tags & rec_tags:
                    recommended_ads.append(ad)

        except Exception as e:
            print(f"DEBUG [Ad]: Advertisement analysis failed: {e}", flush=True)

        elapsed_time = time.time() - start_time
        print(f"DEBUG [Ad]: Finished in {elapsed_time:.2f}s. Found {len(recommended_ads)} ads.", flush=True)
        return recommended_ads

    # 定义异步流式生成器
    async def generate():
        # 在后台启动广告分析
        interest_tag = get_user_tags(memory_system)
        print("interest_tag:", interest_tag, flush=True)
        
        # 在线程池中执行广告分析
        loop = asyncio.get_event_loop()
        ad_future = loop.run_in_executor(
            executor,
            advertise, memory_system, user_id, interest_tag, user_input
        )

        try:
            # 优先处理聊天流
            for chunk in memory_system.get_response_stream(user_input):
                yield f"data: {json.dumps({'response': chunk}, ensure_ascii=False)}\n\n"
            
            # 发送文字结束信号
            yield f"data: {json.dumps({'text_done': True})}\n\n"
            
            # 获取广告结果
            try:
                ad_res = await asyncio.wait_for(ad_future, timeout=20.0)
                if ad_res:
                    print(f"DEBUG [Ad]: Sending {len(ad_res)} ads to frontend", flush=True)
                    yield f"data: {json.dumps({'advertise': ad_res}, ensure_ascii=False)}\n\n"
                else:
                    print(f"DEBUG [Ad]: No ads returned", flush=True)
            except asyncio.TimeoutError:
                print(f"DEBUG [Ad]: Ad calculation timed out after 20 seconds", flush=True)
            except Exception as e:
                print(f"DEBUG [Ad]: Ad calculation failed with error: {type(e).__name__}: {e}", flush=True)
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            print(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')

@app.post('/import_from_cache')
async def import_from_cache_endpoint(request_data: ImportCacheRequest, memory_system: Memcontext = Depends(get_memory_system)):
    """从 temp_memory 缓存直接导入，跳过 videorag 解析"""
    try:
        file_id = request_data.file_id.strip()
        
        if not file_id:
            raise HTTPException(status_code=400, detail='file_id is required')
        
        # 检查缓存文件
        cache_dir = Path(memory_system.data_storage_path) / "temp_memory"
        cache_file = cache_dir / f"{file_id}.json"
        
        if not cache_file.exists():
            raise HTTPException(status_code=404, detail=f'Cache file not found for file_id: {file_id}')
        
        # 加载缓存
        with open(cache_file, "r", encoding="utf-8") as f:
            cached = json.load(f)
        
        # 构建 ConversionOutput
        from memcontext.multimodal.converter import ConversionChunk, ConversionOutput
        
        cached_chunks = []
        for idx, ch in enumerate(cached.get("chunks", [])):
            meta = ch.get("metadata", {}) or {}
            chunk_idx = meta.get("chunk_index", idx)
            cached_chunks.append(
                ConversionChunk(
                    text=ch.get("text", ""),
                    chunk_index=chunk_idx,
                    metadata=meta,
                )
            )
        
        output = ConversionOutput(
            status="success",
            text="\n\n".join(c.text for c in cached_chunks),
            chunks=cached_chunks,
            metadata=cached.get("metadata", {}),
        )
        output.ensure_chunks()
        
        base_metadata = cached.get("metadata", {})
        timestamps = []
        memories_to_add = []
        
        for chunk in output.chunks:
            try:
                base_meta = base_metadata if isinstance(base_metadata, dict) else {}
                chunk_meta_dict = chunk.metadata if isinstance(chunk.metadata, dict) else {}
                
                chunk_meta = {
                    **base_meta,
                    **chunk_meta_dict,
                    "source_type": "multimodal",
                }
            except (TypeError, AttributeError) as e:
                print(f"Import cache: Error merging metadata: {e}")
                chunk_meta = {"source_type": "multimodal"}
            
            if chunk_meta.get("video_path") or chunk_meta.get("video_name"):
                chunk_agent_response = chunk.text
            else:
                chunk_agent_response = chunk_meta.get(
                    "chunk_summary",
                    f"[Multimodal] Stored content from {chunk_meta.get('original_filename', 'file')}",
                )
            
            try:
                video_path = chunk_meta.get("video_path") or chunk_meta.get("original_filename") or chunk_meta.get("video_name") or "视频"
                time_range = chunk_meta.get("time_range", "")
                
                if (chunk_meta.get("video_path") or chunk_meta.get("video_name")) and time_range:
                    if not isinstance(video_path, str) or not video_path or video_path == "视频":
                        video_path = chunk_meta.get("video_name") or chunk_meta.get("original_filename") or "视频"
                    if not isinstance(video_path, str):
                        video_path = str(video_path) if video_path else "视频"
                    user_input = f"描述{video_path}视频的{time_range}的内容"
                else:
                    user_input = chunk.text
            except Exception as e:
                print(f"Import cache: Error building user_input: {e}, using chunk.text as fallback")
                user_input = chunk.text
                video_path = "视频"
            
            memories_to_add.append({
                "user_input": user_input,
                "agent_response": chunk_agent_response,
                "timestamp": get_timestamp(),
                "meta_data": chunk_meta,
            })
            timestamps.append(get_timestamp())
        
        # 使用正常流程：逐个添加到 short_term
        for mem in memories_to_add:
            memory_system.add_memory(
                user_input=mem["user_input"],
                agent_response=mem["agent_response"],
                timestamp=mem["timestamp"],
                meta_data=mem["meta_data"]
            )
        
        return {
            'success': True,
            'ingested_rounds': len(memories_to_add),
            'file_id': file_id,
            'timestamps': timestamps,
            'message': f'Successfully imported {len(memories_to_add)} chunks from cache'
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f'导入缓存失败: {str(e)}'
        )

@app.post('/add_multimodal_memory_stream')
async def add_multimodal_memory_stream(request: Request, memory_system: Memcontext = Depends(get_memory_system)):
    """流式返回视频处理进度的端点"""
    import queue
    import threading
    
    data = await request.json()
    
    file_path = data.get('file_path')
    converter_type = (data.get('converter_type') or 'video').lower()
    agent_response = data.get('agent_response')
    converter_kwargs = data.get('converter_kwargs', {})
    
    if not file_path:
        async def error_gen():
            yield f"data: {json.dumps({'error': 'file_path is required'})}\n\n"
        return StreamingResponse(error_gen(), media_type='text/event-stream')
    
    progress_queue = queue.Queue()
    
    def progress_callback(progress: float, message: str) -> None:
        progress_queue.put({'progress': round(float(progress), 4), 'message': message})
    
    result_holder = {'result': None, 'error': None}
    
    def process_video():
        try:
            converter_settings = dict(converter_kwargs or {})
            converter_settings.setdefault('working_dir', './videorag-workdir')
            result = memory_system.add_multimodal_memory(
                source=file_path,
                source_type='file_path',
                converter_type=converter_type,
                agent_response=agent_response,
                converter_kwargs=converter_settings,
                progress_callback=progress_callback,
            )
            result_holder['result'] = result
        except Exception as e:
            result_holder['error'] = str(e)
        finally:
            progress_queue.put(None)
    
    async def generate():
        loop = asyncio.get_event_loop()
        thread = threading.Thread(target=process_video)
        thread.start()
        
        while True:
            try:
                item = await loop.run_in_executor(None, progress_queue.get, True, 0.5)
                if item is None:
                    break
                yield f"data: {json.dumps(item)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
        
        thread.join()
        
        if result_holder['error']:
            yield f"data: {json.dumps({'done': True, 'error': result_holder['error']})}\n\n"
        else:
            res = result_holder['result']
            yield f"data: {json.dumps({'done': True, 'success': True, 'chunks_written': res.get('chunks_written', 0), 'file_id': res.get('file_id')})}\n\n"
    
    return StreamingResponse(generate(), media_type='text/event-stream')

@app.post('/add_multimodal_memory')
async def add_multimodal_memory_endpoint(request: Request, memory_system: Memcontext = Depends(get_memory_system)):
    cleanup_paths = []

    try:
        converter_type = None
        agent_response = None
        converter_kwargs = {}

        content_type = request.headers.get('content-type', '')
        if 'multipart/form-data' in content_type:
            form = await request.form()
            uploaded_file = form.get('file')
            if not uploaded_file:
                raise HTTPException(status_code=400, detail='File upload is required.')
            
            safe_name = secure_filename(uploaded_file.filename)
            temp_dir = tempfile.mkdtemp(prefix="memcontext_upload_")
            temp_path = os.path.join(temp_dir, safe_name or "upload.bin")
            
            # 保存文件
            with open(temp_path, 'wb') as f:
                content = await uploaded_file.read()
                f.write(content)
            
            cleanup_paths.append(temp_dir)

            source = temp_path
            source_type = 'file_path'
            agent_response = form.get('agent_response')
            converter_type = form.get('converter_type')
            if form.get('converter_kwargs'):
                try:
                    converter_kwargs = json.loads(form.get('converter_kwargs'))
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail='converter_kwargs must be valid JSON')
        else:
            data = await request.json()
            if data.get('file_path'):
                source = data['file_path']
                source_type = 'file_path'
            elif data.get('url'):
                source = data['url']
                source_type = 'url'
            else:
                raise HTTPException(status_code=400, detail='file_path or url must be provided')

            converter_type = data.get('converter_type')
            agent_response = data.get('agent_response')
            converter_kwargs = data.get('converter_kwargs', {})

        if source_type != 'file_path':
            raise HTTPException(status_code=400, detail='当前仅支持本地文件路径(file_path)的视频源')

        converter_type = (converter_type or 'videorag').lower()
        if converter_type not in ('video', 'videorag'):
            raise HTTPException(status_code=400, detail=f'不支持的 converter_type: {converter_type}，可选 video | videorag')

        converter_settings = dict(converter_kwargs or {})
        converter_settings.pop('deepseek_key', None)
        converter_settings.pop('siliconflow_key', None)

        converter_settings.setdefault('working_dir', './videorag-workdir')
        progress_events = []

        def progress_callback(progress: float, message: str) -> None:
            progress_events.append({
                'progress': round(float(progress), 4),
                'message': message
            })

        try:
            result = memory_system.add_multimodal_memory(
                source=source,
                source_type=source_type,
                converter_type=converter_type,
                agent_response=agent_response,
                converter_kwargs=converter_settings,
                progress_callback=progress_callback,
            )
            
            if result.get('status') != 'success':
                raise HTTPException(
                    status_code=500,
                    detail=result.get('error', '处理失败')
                )

            response_data = {
                'success': True,
                'ingested_rounds': result.get('chunks_written', 0),
                'file_id': result.get('file_id'),
                'timestamps': result.get('timestamps', []),
                'progress': progress_events
            }
            if result.get('storage_path'):
                response_data['storage_path'] = result.get('storage_path')
            if result.get('storage_base_path'):
                response_data['storage_base_path'] = result.get('storage_base_path')
            return response_data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f'调用 add_multimodal_memory 失败: {str(e)}'
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in cleanup_paths:
            try:
                shutil.rmtree(path, ignore_errors=True)
            except Exception:
                pass

@app.get('/memory_state')
async def get_memory_state(memory_system: Memcontext = Depends(get_memory_system)):
    try:
        short_term = memory_system.short_term_memory.get_all()
        mid_term_sessions = []
        for sid, session_data in list(memory_system.mid_term_memory.sessions.items())[:5]:
            mid_term_sessions.append({
                'id': sid,
                'summary': session_data.get('summary', ''),
                'keywords': session_data.get('summary_keywords', []),
                'heat': session_data.get('H_segment', 0),
                'visit_count': session_data.get('N_visit', 0),
                'last_visit': session_data.get('last_visit_time', ''),
                'page_count': len(session_data.get('details', []))
            })
        
        mid_term_sessions.sort(key=lambda x: x['heat'], reverse=True)
        
        user_profile = memory_system.user_long_term_memory.get_raw_user_profile(memory_system.user_id)
        user_knowledge = memory_system.user_long_term_memory.get_user_knowledge()
        assistant_knowledge = memory_system.assistant_long_term_memory.get_assistant_knowledge()
        return {
            'short_term': {
                'capacity': memory_system.short_term_memory.max_capacity,
                'current_count': len(short_term),
                'memories': short_term
            },
            'mid_term': {
                'capacity': memory_system.mid_term_memory.max_capacity,
                'current_count': len(memory_system.mid_term_memory.sessions),
                'sessions': mid_term_sessions,
                'heat_threshold': memory_system.mid_term_heat_threshold
            },
            'long_term': {
                'user_profile': user_profile,
                'user_knowledge': [k.get('knowledge', '') for k in user_knowledge],
                'assistant_knowledge': [k.get('knowledge', '') for k in assistant_knowledge]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/trigger_analysis')
async def trigger_analysis(memory_system: Memcontext = Depends(get_memory_system)):
    try:
        if not memory_system.mid_term_memory.sessions:
            raise HTTPException(status_code=400, detail='No Mid-term memory, but at least keep short-term memory for seven rounds.')
        
        has_unanalyzed_pages = False
        for session_data in memory_system.mid_term_memory.sessions.values():
            unanalyzed_pages = [p for p in session_data.get('details', []) if not p.get('analyzed', False)]
            if unanalyzed_pages:
                has_unanalyzed_pages = True
                break
        
        if not has_unanalyzed_pages:
            raise HTTPException(status_code=400, detail='No Mid-term memory, but at least keep short-term memory for seven rounds.')
        
        memory_system.force_mid_term_analysis()
        return {'success': True, 'message': 'Analysis triggered successfully'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/personality_analysis')
async def personality_analysis(memory_system: Memcontext = Depends(get_memory_system)):
    try:
        user_profile = memory_system.user_long_term_memory.get_raw_user_profile(memory_system.user_id)
        
        if not user_profile or user_profile.lower() in ['none', 'no profile data yet']:
            raise HTTPException(status_code=400, detail='No user profile available for analysis')
        
        personality_analysis_result = parse_personality_traits(user_profile)
        
        return {
            'success': True,
            'personality_analysis': personality_analysis_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def parse_personality_traits(user_profile):
    """Parse personality traits from user profile text."""
    categories = {
        'Psychological Model': [
            'Extraversion', 'Openness', 'Agreeableness', 'Conscientiousness', 'Neuroticism',
            'Physiological Needs', 'Need for Security', 'Need for Belonging', 'Need for Self-Esteem',
            'Cognitive Needs', 'Aesthetic Appreciation', 'Self-Actualization', 'Need for Order',
            'Need for Autonomy', 'Need for Power', 'Need for Achievement'
        ],
        'AI Alignment Dimensions': [
            'Helpfulness', 'Honesty', 'Safety', 'Instruction Compliance', 'Truthfulness',
            'Coherence', 'Complexity', 'Conciseness'
        ],
        'Content Platform Interest Tags': [
            'Science Interest', 'Education Interest', 'Psychology Interest', 'Family Concern',
            'Fashion Interest', 'Art Interest', 'Health Concern', 'Financial Management Interest',
            'Sports Interest', 'Food Interest', 'Travel Interest', 'Music Interest',
            'Literature Interest', 'Film Interest', 'Social Media Activity', 'Tech Interest',
            'Environmental Concern', 'History Interest', 'Political Concern', 'Religious Interest',
            'Gaming Interest', 'Animal Concern', 'Emotional Expression', 'Sense of Humor',
            'Information Density', 'Language Style', 'Practicality'
        ]
    }
    
    extracted_traits = {}
    
    pattern = r'([A-Za-z\s]+)\s*\(\s*([A-Za-z]+)\s*\)'
    matches = re.findall(pattern, user_profile)
    
    for match in matches:
        dimension = match[0].strip()
        level = match[1].strip()
        
        for category, dimensions in categories.items():
            for cat_dimension in dimensions:
                if dimension.lower() in cat_dimension.lower() or cat_dimension.lower() in dimension.lower():
                    if category not in extracted_traits:
                        extracted_traits[category] = []
                    extracted_traits[category].append({
                        'dimension': dimension,
                        'level': level
                    })
                    break
    
    lines = user_profile.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        for level in ['High', 'Medium', 'Low']:
            if level.lower() in line.lower():
                for category, dimensions in categories.items():
                    for dimension in dimensions:
                        if dimension.lower() in line.lower():
                            if category not in extracted_traits:
                                extracted_traits[category] = []
                            
                            existing = [t for t in extracted_traits[category] if t['dimension'] == dimension]
                            if not existing:
                                extracted_traits[category].append({
                                    'dimension': dimension,
                                    'level': level
                                })
                            break
    
    return extracted_traits

@app.post('/clear_memory')
async def clear_memory(request: Request, memory_system: Memcontext = Depends(get_memory_system)):
    session_id = await get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=400, detail='Session ID not found')
    
    try:
        user_data_dir = memory_system.user_data_dir
        assistant_data_dir = memory_system.assistant_data_dir
        
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
        
        if os.path.exists(assistant_data_dir):
            shutil.rmtree(assistant_data_dir)
        
        config = session_storage.get(session_id, {}).get('memory_config')
        if not config:
            raise HTTPException(status_code=400, detail='Configuration not found in session. Please re-initialize.')

        api_key = config['api_key']
        base_url = config['base_url']
        model = config['model']
        user_id = memory_system.user_id
        assistant_id = memory_system.assistant_id
        data_path = memory_system.data_storage_path
        embedding_model = os.environ.get('EMBEDDING_MODEL', 'doubao-embedding-large-text-250515').strip()
        
        new_memory_system = Memcontext(
            user_id=user_id,
            openai_api_key=api_key,
            openai_base_url=base_url,
            data_storage_path=data_path,
            assistant_id=assistant_id,
            short_term_capacity=7,
            mid_term_capacity=200,
            long_term_knowledge_capacity=100,
            mid_term_heat_threshold=5.0,
            llm_model=model,
            embedding_model_name=embedding_model, 
            embedding_model_kwargs={}
        )
        
        memory_systems[session_id] = new_memory_system
        
        return {'success': True, 'message': 'All memories cleared successfully'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/import_conversations')
async def import_conversations(request_data: ImportConversationsRequest, memory_system: Memcontext = Depends(get_memory_system)):
    conversations = request_data.conversations
    
    if not conversations:
        raise HTTPException(status_code=400, detail='No conversations provided')
    
    try:
        imported_count = 0
        for conv in conversations:
            user_input = conv.get('user_input', '')
            agent_response = conv.get('agent_response', '')
            timestamp = conv.get('timestamp', get_timestamp())
            
            if user_input and agent_response:
                memory_system.add_memory(
                    user_input=user_input,
                    agent_response=agent_response,
                    timestamp=timestamp
                )
                imported_count += 1
            else:
                print(f"Skipping invalid conversation: {conv}")
        
        return {
            'success': True,
            'imported_count': imported_count,
            'message': f'Successfully imported {imported_count} conversations'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5019)
