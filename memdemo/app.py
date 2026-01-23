# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session,Response, stream_with_context
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=5)

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
# load_dotenv 会自动从当前目录和父目录向上查找 .env 文件
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add parent directory to path to import memcontext
# Ensure the path is /root/autodl-tmp for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import memcontext modules directly
from memcontext import Memcontext
# Import utils directly from the playground directory
from memcontext.utils import get_timestamp

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# CORS 配置 - 允许跨域请求
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Global memcontext instance (in production, you'd use proper session management)
memory_systems = {}


# 商品数据(用于广告推荐)
ad_data_dir = os.path.join(os.path.dirname(__file__), 'ad_data')
with open(os.path.join(ad_data_dir, 'ad_demo_format.json'), 'r', encoding='utf-8') as f: 
    ads_data = json.load(f)
    ads_data = ads_data["advertisements"]
with open(os.path.join(ad_data_dir, 'forbidden_keywords.json'), 'r', encoding='utf-8') as f: 
    forbidden_keywords = json.load(f)
    forbidden_keywords = forbidden_keywords.get("forbidden_words", forbidden_keywords.get("forbidden_keywords", []))

interest_log = {}


# 删除了固定的API_KEY, BASE_URL, MODEL

# 有效邀请码列表 - 在实际部署中应该存储在数据库或加密文件中
# VALID_INVITE_CODES = [
#     'DEMO2024',
#     'MEMORY001',
#     'TESTUSER',
#     'BETA2024',
#     'INVITE123'
# ]

# def load_invite_codes():
#     """从文件加载邀请码列表"""
#     invite_codes_file = os.path.join(os.path.dirname(__file__), 'invite_codes.json')
#     try:
#         if os.path.exists(invite_codes_file):
#             with open(invite_codes_file, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         else:
#             # 如果文件不存在，创建默认邀请码文件
#             with open(invite_codes_file, 'w', encoding='utf-8') as f:
#                 json.dump(VALID_INVITE_CODES, f, ensure_ascii=False, indent=2)
#             return VALID_INVITE_CODES
#     except Exception as e:
#         print(f"Error loading invite codes: {e}")
#         return VALID_INVITE_CODES

# def save_invite_codes(codes):
#     """保存邀请码列表到文件"""
#     invite_codes_file = os.path.join(os.path.dirname(__file__), 'invite_codes.json')
#     try:
#         with open(invite_codes_file, 'w', encoding='utf-8') as f:
#             json.dump(codes, f, ensure_ascii=False, indent=2)
#     except Exception as e:
#         print(f"Error saving invite codes: {e}")

# 启动时加载邀请码
# VALID_INVITE_CODES = load_invite_codes()

# 处理 OPTIONS 预检请求
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

@app.route('/')
def index():
    return "MemContext API Server is running. Please access the frontend via the Vite development server or the built static files."

@app.route('/init_memory', methods=['POST'])
def init_memory():
    data = request.json
    user_id = data.get('user_id', '').strip()
    # 豆包配置从环境变量读取
    api_key = os.environ.get('LLM_API_KEY', '').strip()
    base_url = os.environ.get('LLM_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3').strip()
    model = os.environ.get('LLM_MODEL', 'doubao-seed-1-6-flash-250828').strip()
    embedding_model = os.environ.get('EMBEDDING_MODEL', 'doubao-embedding-large-text-250515').strip()

    if not user_id:
        return jsonify({'error': 'User ID 是必需的。'}), 400
    
    if not api_key:
        return jsonify({'error': 'LLM_API_KEY 环境变量未配置，请设置豆包 API Key。'}), 400
    
    assistant_id = f"assistant_{user_id}"
    
    try:
        # Initialize memcontext for this session
        data_path = './data'
        os.makedirs(data_path, exist_ok=True)
        
        # 获取 file_storage_base_path（可选，默认使用项目根目录）
        file_storage_base_path = data.get('file_storage_base_path', '').strip()
        if not file_storage_base_path:
            # 默认使用项目根目录，FileStorageManager 会在根目录下创建 files 目录
            # app.py 在 memdemo/ 目录下，所以上一级目录就是项目根目录
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            file_storage_base_path = project_root
        
        memory_system = Memcontext(
            user_id=user_id,
            openai_api_key=api_key,
            openai_base_url=base_url,
            data_storage_path=data_path,
            assistant_id=assistant_id,  # 使用邀请码作为assistant_id
            short_term_capacity=7,  # Smaller for demo
            mid_term_capacity=200,   # Smaller for demo
            long_term_knowledge_capacity=1000,  # Smaller for demo
            mid_term_heat_threshold=10.0,
            embedding_model_name=embedding_model,
            embedding_model_kwargs={},
            llm_model=model,
            file_storage_base_path=file_storage_base_path
        )
        
        session_id = secrets.token_hex(8)
        memory_systems[session_id] = memory_system
        session['memory_session_id'] = session_id
        # 将配置存入session
        session['memory_config'] = {
            'api_key': api_key,
            'base_url': base_url,
            'model': model,
            'embedding_provider': 'doubao'
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_id': user_id,
            'assistant_id': assistant_id,
            'model': model,
            'base_url': base_url,
            'embedding_provider': session['memory_config']['embedding_provider']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_user_tags(memory_system):
    """获取用户标签
    return 字典 {'interests':["兴趣1","兴趣2"],
    "personality_traits":["性格1","性格2"]}"""
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

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    user_id = data.get('user_id', '').strip()
    
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]

    def advertise(mem_sys, uid, tags, current_input):
        print(f"DEBUG [Ad]: advertise task started for user={uid}", flush=True)
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
        
        context_str = ""
        if short_term_memories:
            for mem in short_term_memories[-5:]: 
                u_in = mem.get('user_input', '')
                a_res = mem.get('agent_response', '')
                context_str += f"User: {u_in}\nAI: {a_res}\n"
        
        # 5. 构建 Prompt (修正：使用参数 tags 和 current_input)
        prompt = (
            f"你是一个广告匹配引擎的语义分析器。\n"
            f"用户当前的显式兴趣标签是：{','.join(tags)}。\n"
            f"用户最近的对话上下文是：\n{context_str}\n"
            f"用户本轮输入：\n{current_input}\n\n"
            f"任务：分析用户的潜在需求，提取 2-3 个宏观主题(topics) 和 3-5 个具体关键词(keywords)。\n"
            f"主题(topics)请尽量使用中文通用词（如运动, 科技, 食品, 健康）。\n"
            f"关键词(keywords)请使用中文，对应具体商品品类或属性。\n\n"
            f"**必须且只能**返回合法的 JSON 格式，不要包含任何其他文字。格式示例：\n"
            f'{{"topics": ["运动", "健康"], "keywords": ["跑鞋", "护膝", "减肥"]}}'
        )

        try:
            print(f"DEBUG [Ad]: Calling LLM for ad analysis...", flush=True)
            recommendation = mem_sys.client.chat_completion(
                model=mem_sys.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                stream=False
            )
            print(f"DEBUG [Ad]: LLM Response: {recommendation[:100]}...", flush=True)
            
            extracted_data = None
            try:
                extracted_data = json.loads(recommendation)
            except:
                import re
                extracted_data = re.sub(r"```json\s*|\s*```", "", recommendation, flags=re.IGNORECASE).strip()
                extracted_data = json.loads(extracted_data)

            if extracted_data:
                rec_topics = set(t.lower() for t in extracted_data.get('topics', []) if t.lower() not in forbidden_keywords)
                rec_keywords = set(k.lower() for k in extracted_data.get('keywords', []) if k.lower() not in forbidden_keywords)
                print(f"DEBUG [Ad]: AI Extracted: Topics={rec_topics}, Keywords={rec_keywords}", flush=True)
            else:
                print("DEBUG [Ad]: Failed to parse JSON from LLM response", flush=True)

        except Exception as e:
            print(f"DEBUG [Ad]: Failed to parse advertisement analysis response: {e}", flush=True)

        for ad in ads_data:
            ad_topics = set(t.lower() for t in ad.get('topics', []))
            ad_keywords = set(k.lower() for k in ad.get('keywords', []))
            
            if (ad_topics & rec_topics) or (ad_keywords & rec_keywords):
                recommended_ads.append(ad)

        print(f"DEBUG [Ad]: Finished. Found {len(recommended_ads)} ads.", flush=True)
        return recommended_ads

    # 定义流式生成器 
    def generate():
        # 立即在后台启动广告分析 (不阻塞聊天)
        interest_tag = get_user_tags(memory_system)
        print("interest_tag:", interest_tag, flush=True)
        ad_future = executor.submit(
            advertise, memory_system,user_id, interest_tag,user_input
        )

        try:
            # 优先处理聊天流 (用户立刻看到字)
            for chunk in memory_system.get_response_stream(user_input):
                # 包装成 SSE 格式: data: {...}\n\n
                yield f"data: {json.dumps({'response': chunk}, ensure_ascii=False)}\n\n"
            
            # 发送文字结束信号，让前端可以提前解锁输入框
            yield f"data: {json.dumps({'text_done': True})}\n\n"
            
            # 聊天结束，获取广告结果
            try:
                ad_res = ad_future.result(timeout=5) 
                if ad_res:
                    yield f"data: {json.dumps({'advertise': ad_res}, ensure_ascii=False)}\n\n"
            except Exception as e:
                print(f"Ad calculation timed out or failed: {e}")
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            print(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/import_from_cache', methods=['POST'])
def import_from_cache_endpoint():
    """从 temp_memory 缓存直接导入，跳过 videorag 解析"""
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400

    memory_system = memory_systems[session_id]
    
    try:
        data = request.get_json(silent=True) or {}
        file_id = data.get('file_id', '').strip()
        
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        # 检查缓存文件
        cache_dir = Path(memory_system.data_storage_path) / "temp_memory"
        cache_file = cache_dir / f"{file_id}.json"
        
        if not cache_file.exists():
            return jsonify({'error': f'Cache file not found for file_id: {file_id}'}), 404
        
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
        
        # 直接使用 _ingest_single_multimodal 的逻辑来添加记忆
        base_metadata = cached.get("metadata", {})
        timestamps = []
        memories_to_add = []
        
        for chunk in output.chunks:
            # 安全地合并元数据，确保所有值都是字典
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
            
            # 对于视频内容，使用完整的文本描述（chunk.text）作为 agent_response
            # 这样检索时能获得详细的视频内容，而不是只有摘要
            if chunk_meta.get("video_path") or chunk_meta.get("video_name"):
                chunk_agent_response = chunk.text  # 使用完整的视频描述文本
            else:
                chunk_agent_response = chunk_meta.get(
                    "chunk_summary",
                    f"[Multimodal] Stored content from {chunk_meta.get('original_filename', 'file')}",
                )
            
            # 对于视频内容，构建格式化的 user_input
            # 安全获取 video_path，确保不会为 None 或抛出 KeyError
            try:
                video_path = chunk_meta.get("video_path") or chunk_meta.get("original_filename") or chunk_meta.get("video_name") or "视频"
                time_range = chunk_meta.get("time_range", "")
                
                if (chunk_meta.get("video_path") or chunk_meta.get("video_name")) and time_range:
                    # 确保 video_path 是字符串且不为空
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
                video_path = "视频"  # 设置默认值
            
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
        
        return jsonify({
            'success': True,
            'ingested_rounds': len(memories_to_add),
            'file_id': file_id,
            'timestamps': timestamps,
            'message': f'Successfully imported {len(memories_to_add)} chunks from cache'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': f'导入缓存失败: {str(e)}',
            'traceback': traceback.format_exc() if app.debug else None
        }), 500

@app.route('/add_multimodal_memory_stream', methods=['POST'])
def add_multimodal_memory_stream():
    """流式返回视频处理进度的端点"""
    from flask import Response, stream_with_context
    import queue
    import threading
    
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        def error_gen():
            yield f"data: {json.dumps({'error': 'Memory system not initialized'})}\n\n"
        return Response(error_gen(), mimetype='text/event-stream')
    
    memory_system = memory_systems[session_id]
    data = request.get_json(silent=True) or {}
    
    file_path = data.get('file_path')
    converter_type = (data.get('converter_type') or 'video').lower()
    agent_response = data.get('agent_response')
    converter_kwargs = data.get('converter_kwargs', {})
    
    if not file_path:
        def error_gen():
            yield f"data: {json.dumps({'error': 'file_path is required'})}\n\n"
        return Response(error_gen(), mimetype='text/event-stream')
    
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
            progress_queue.put(None)  # 信号结束
    
    def generate():
        thread = threading.Thread(target=process_video)
        thread.start()
        
        while True:
            try:
                item = progress_queue.get(timeout=0.5)
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
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/add_multimodal_memory', methods=['POST'])
def add_multimodal_memory_endpoint():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400

    memory_system = memory_systems[session_id]
    cleanup_paths = []

    try:
        converter_type = None
        agent_response = None
        converter_kwargs = {}

        if request.content_type and 'multipart/form-data' in request.content_type:
            uploaded_file = request.files.get('file')
            if not uploaded_file or not uploaded_file.filename:
                return jsonify({'error': 'File upload is required.'}), 400

            safe_name = secure_filename(uploaded_file.filename)
            temp_dir = tempfile.mkdtemp(prefix="memcontext_upload_")
            temp_path = os.path.join(temp_dir, safe_name or "upload.bin")
            uploaded_file.save(temp_path)
            cleanup_paths.append(temp_dir)

            source = temp_path
            source_type = 'file_path'
            agent_response = request.form.get('agent_response')
            converter_type = request.form.get('converter_type')
            if request.form.get('converter_kwargs'):
                try:
                    converter_kwargs = json.loads(request.form['converter_kwargs'])
                except json.JSONDecodeError:
                    return jsonify({'error': 'converter_kwargs must be valid JSON'}), 400
        else:
            data = request.get_json(silent=True) or {}
            if data.get('file_path'):
                source = data['file_path']
                source_type = 'file_path'
            elif data.get('url'):
                source = data['url']
                source_type = 'url'
            else:
                return jsonify({'error': 'file_path or url must be provided'}), 400

            converter_type = data.get('converter_type')
            agent_response = data.get('agent_response')
            converter_kwargs = data.get('converter_kwargs', {})

        if source_type != 'file_path':
            return jsonify({'error': '当前仅支持本地文件路径(file_path)的视频源'}), 400

        converter_type = (converter_type or 'videorag').lower()
        if converter_type not in ('video', 'videorag'):
            return jsonify({'error': f'不支持的 converter_type: {converter_type}，可选 video | videorag'}), 400

        converter_settings = dict(converter_kwargs or {})
        # 移除不再使用的 deepseek_key 和 siliconflow_key
        converter_settings.pop('deepseek_key', None)
        converter_settings.pop('siliconflow_key', None)

        converter_settings.setdefault('working_dir', './videorag-workdir')
        progress_events = []

        def progress_callback(progress: float, message: str) -> None:
            progress_events.append({
                'progress': round(float(progress), 4),
                'message': message
            })

        # 使用 memory_system.add_multimodal_memory() 方法，它会自动处理所有chunks并存储到记忆中
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
                return jsonify({
                    'error': result.get('error', '处理失败'),
                    'metadata': result,
                    'progress': progress_events
                }), 500

            response_data = {
                'success': True,
                'ingested_rounds': result.get('chunks_written', 0),
                'file_id': result.get('file_id'),
                'timestamps': result.get('timestamps', []),
                'progress': progress_events
            }
            # 如果有存储路径信息，也返回
            if result.get('storage_path'):
                response_data['storage_path'] = result.get('storage_path')
            if result.get('storage_base_path'):
                response_data['storage_base_path'] = result.get('storage_base_path')
            return jsonify(response_data)
        except Exception as e:
            return jsonify({
                'error': f'调用 add_multimodal_memory 失败: {str(e)}',
                'progress': progress_events
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        for path in cleanup_paths:
            try:
                shutil.rmtree(path, ignore_errors=True)
            except Exception:
                pass

@app.route('/memory_state', methods=['GET'])
def get_memory_state():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Get short-term memory
        short_term = memory_system.short_term_memory.get_all()
        mid_term_sessions = []
        # Get mid-term memory sessions (top 5)
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
        
        # Sort by heat
        mid_term_sessions.sort(key=lambda x: x['heat'], reverse=True)
        
        # Get long-term memory - separate user profile, user knowledge, and assistant knowledge
        user_profile = memory_system.user_long_term_memory.get_raw_user_profile(memory_system.user_id)
        user_knowledge = memory_system.user_long_term_memory.get_user_knowledge()
        assistant_knowledge = memory_system.assistant_long_term_memory.get_assistant_knowledge()
        return jsonify({
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
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trigger_analysis', methods=['POST'])
def trigger_analysis():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Check if there are any mid-term memory sessions to analyze
        if not memory_system.mid_term_memory.sessions:
            return jsonify({'error': 'No Mid-term memory, but at least keep short-term memory for seven rounds.'}), 400
        
        # Check if there are any unanalyzed pages in mid-term memory
        has_unanalyzed_pages = False
        for session_data in memory_system.mid_term_memory.sessions.values():
            unanalyzed_pages = [p for p in session_data.get('details', []) if not p.get('analyzed', False)]
            if unanalyzed_pages:
                has_unanalyzed_pages = True
                break
        
        if not has_unanalyzed_pages:
            return jsonify({'error': 'No Mid-term memory, but at least keep short-term memory for seven rounds.'}), 400
        
        # Force mid-term analysis
        memory_system.force_mid_term_analysis()
        return jsonify({'success': True, 'message': 'Analysis triggered successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/personality_analysis', methods=['POST'])
def personality_analysis():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Get user profile
        user_profile = memory_system.user_long_term_memory.get_raw_user_profile(memory_system.user_id)
        
        if not user_profile or user_profile.lower() in ['none', 'no profile data yet']:
            return jsonify({'error': 'No user profile available for analysis'}), 400
        
        # Parse personality traits from the user profile
        personality_analysis = parse_personality_traits(user_profile)
        
        return jsonify({
            'success': True,
            'personality_analysis': personality_analysis
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_personality_traits(user_profile):
    """
    Parse personality traits from user profile text.
    Extract traits in format: Dimension ( Level(High/Medium/Low) )
    """
    # Define the three main categories
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
    
    # Extract traits from user profile
    extracted_traits = {}
    
    import re
    
    # Look for patterns like "Dimension ( Level(High/Medium/Low) )"
    pattern = r'([A-Za-z\s]+)\s*\(\s*([A-Za-z]+)\s*\)'
    matches = re.findall(pattern, user_profile)
    
    for match in matches:
        dimension = match[0].strip()
        level = match[1].strip()
        
        # Find which category this dimension belongs to
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
    
    # Alternative pattern: look for lines containing trait descriptions
    lines = user_profile.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for mentions of High/Medium/Low levels
        for level in ['High', 'Medium', 'Low']:
            if level.lower() in line.lower():
                # Try to extract the dimension name
                for category, dimensions in categories.items():
                    for dimension in dimensions:
                        if dimension.lower() in line.lower():
                            if category not in extracted_traits:
                                extracted_traits[category] = []
                            
                            # Check if this trait is already added
                            existing = [t for t in extracted_traits[category] if t['dimension'] == dimension]
                            if not existing:
                                extracted_traits[category].append({
                                    'dimension': dimension,
                                    'level': level
                                })
                            break
    
    return extracted_traits

@app.route('/clear_memory', methods=['POST'])
def clear_memory():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Clear all memory files
        user_data_dir = memory_system.user_data_dir
        assistant_data_dir = memory_system.assistant_data_dir
        
        # Remove the entire user data directory
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
        
        # Remove the entire assistant data directory  
        if os.path.exists(assistant_data_dir):
            shutil.rmtree(assistant_data_dir)
        
        # 从session中获取配置来重新初始化
        config = session.get('memory_config')
        if not config:
            return jsonify({'error': 'Configuration not found in session. Please re-initialize.'}), 400

        api_key = config['api_key']
        base_url = config['base_url']
        model = config['model']
        user_id = memory_system.user_id
        assistant_id = memory_system.assistant_id
        data_path = memory_system.data_storage_path
        embedding_model = os.environ.get('EMBEDDING_MODEL', 'doubao-embedding-large-text-250515').strip()
        # Create new memory system
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
        
        # Replace the old memory system
        memory_systems[session_id] = new_memory_system
        
        return jsonify({'success': True, 'message': 'All memories cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/import_conversations', methods=['POST'])
def import_conversations():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    data = request.json
    conversations = data.get('conversations', [])
    
    if not conversations:
        return jsonify({'error': 'No conversations provided'}), 400
    
    try:
        imported_count = 0
        for conv in conversations:
            user_input = conv.get('user_input', '')
            agent_response = conv.get('agent_response', '')
            timestamp = conv.get('timestamp', get_timestamp())
            
            if user_input and agent_response:
                # Add each conversation to memory system
                memory_system.add_memory(
                    user_input=user_input,
                    agent_response=agent_response,
                    timestamp=timestamp
                )
                imported_count += 1
            else:
                print(f"Skipping invalid conversation: {conv}")
        
        return jsonify({
            'success': True,
            'imported_count': imported_count,
            'message': f'Successfully imported {imported_count} conversations'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5019) 