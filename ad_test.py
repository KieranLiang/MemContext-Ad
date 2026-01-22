import requests
import json
import sys
import time

# 配置你的后端地址 (根据你的 app.py，端口是 5019)
BASE_URL = "http://127.0.0.1:5019"

def test_chat_stream():
    # 使用 session 对象来自动保持 Cookie (session_id)
    session = requests.Session()

    print(f"1. 正在初始化记忆系统 (User: test_user_001)...")
    try:
        # --- 第一步：初始化 (必须步骤，否则 /chat 会报错) ---
        init_payload = {
            "user_id": "test_user_001"
        }
        init_resp = session.post(f"{BASE_URL}/init_memory", json=init_payload)
        
        if init_resp.status_code == 200:
            print("✅ 初始化成功！Session ID 已获取。")
        else:
            print(f"❌ 初始化失败: {init_resp.text}")
            return
    except Exception as e:
        print(f"❌ 连接服务器失败，请确保 app.py 正在运行。\n错误: {e}")
        return

    # --- 第二步：发送聊天请求并测试流式 + 广告 ---
    print("\n2. 发送聊天请求 (模拟询问运动装备)...")
    
    chat_payload = {
        "message": "最近我想开始晨跑，有没有什么注意事项？还有我膝盖不太好。",
        "user_id": "test_user_001",
        # 故意加上相关标签，触发广告推荐
        "interest_tag": ["运动", "健康", "护具"] 
    }

    try:
        # 【关键】 stream=True 开启流式读取
        response = session.post(f"{BASE_URL}/chat", json=chat_payload, stream=True)
        
        print("\n---⬇️ 模拟前端接收流数据 ⬇️---\n")
        
        full_text = ""
        received_ads = []
        is_stream_working = False

        # iter_lines() 会一行行读取 SSE 数据
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                # SSE 格式通常是以 "data: " 开头
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:] # 去掉前缀
                    
                    try:
                        data = json.loads(json_str)
                        
                        # --- 情况 A: 聊天文字 (response) ---
                        if "response" in data:
                            char = data["response"]
                            # 像打字机一样打印出来，验证流式效果
                            print(char, end="", flush=True) 
                            full_text += char
                            is_stream_working = True
                            
                        # --- 情况 B: 广告数据 (advertise) ---
                        elif "advertise" in data:
                            print("\n\n[🎁 收到广告推送 event!]")
                            received_ads = data["advertise"]
                            # 漂亮地打印广告
                            print(json.dumps(received_ads, indent=2, ensure_ascii=False))
                            
                        # --- 情况 C: 结束信号 (done) ---
                        elif "done" in data:
                            print("\n\n[✅ 流传输结束信号]")
                            
                        # --- 情况 D: 错误 (error) ---
                        elif "error" in data:
                            print(f"\n\n[❌ 流中包含错误]: {data['error']}")

                    except json.JSONDecodeError:
                        print(f"[解析错误]: {decoded_line}")

        # --- 第三步：总结测试结果 ---
        print("\n" + "="*30)
        print("测试报告:")
        print("="*30)
        
        # 验证 1: 是否是流式? (如果不流式，会卡很久才一次性打印，is_stream_working 会在最后才变 True)
        if is_stream_working and len(full_text) > 0:
            print("✅ 流式传输: 正常 (已逐字接收)")
        else:
            print("❌ 流式传输: 失败 (未收到内容)")

        # 验证 2: 是否收到了广告?
        if received_ads and len(received_ads) > 0:
            print(f"✅ 广告推荐: 成功 (收到 {len(received_ads)} 条广告)")
            print(f"   第一条广告标题: {received_ads[0].get('title', 'Unknown')}")
        else:
            print("⚠️ 广告推荐: 未收到 (可能是 LLM 没匹配到，或者逻辑有问题)")

    except Exception as e:
        print(f"\n❌ 请求发生异常: {e}")

if __name__ == "__main__":
    test_chat_stream()