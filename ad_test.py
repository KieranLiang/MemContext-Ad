import requests
import json
import time

# 配置基础 URL
BASE_URL = "http://127.0.0.1:5019"

def run_test():
    # 使用 Session 保持 Cookie (session_id)
    client = requests.Session()
    user_id = "test_user_008"

    print("=== 1. 初始化内存 ===")
    try:
        resp = client.post(f"{BASE_URL}/init_memory", json={"user_id": user_id})
        print(f"Init Status: {resp.status_code}")
        if resp.status_code != 200:
            print("初始化失败，停止测试")
            return
    except Exception as e:
        print(f"连接失败，请确认服务已启动: {e}")
        return

    print("\n=== 2. 注入对话背景 (Short Term Memory) ===")
    # 场景：用户虽然点击了 Interest Tag，但对话内容更具体
    # 我们故意让对话内容指向 'sports' 或 'health'，看看能不能覆盖掉单纯的 interest_tag
    messages = [
        "我最近感觉身体素质太差了，跑两步就喘。",
        "想买个能监测心率的东西，或者买双好点的鞋子开始跑步。"
    ]
    
    for msg in messages:
        resp = client.post(f"{BASE_URL}/chat", json={"message": msg})
        print(f"User sent: {msg}")
        # print(f"AI replied: {resp.json().get('response')}")
        time.sleep(1) # 稍微等一下

    print("\n=== 3. 请求广告接口 (/advertise) ===")
    # 模拟用户点击了 'technology' (科技) 标签
    # 预期：虽然标签是科技，但结合对话(跑步、心率)，LLM 应该能提取出 'sports', 'health', '手环', '鞋' 等关键词
    # 从而推荐 "智能健康手环" (科技+运动) 或 "足球鞋" (运动)
    payload = {
        "user_id": user_id,
        "interest_tag": ["科技","运动","工具"] 
    }
    
    start_time = time.time()
    resp = client.post(f"{BASE_URL}/advertise", json=payload)
    end_time = time.time()
    
    print(f"Status Code: {resp.status_code}")
    print(f"Time Taken: {end_time - start_time:.2f}s")
    
    try:
        result = resp.json()
        print("\n--- 返回结果 ---")
        # 美化打印 JSON
        print(json.dumps(result, indent=4, ensure_ascii=False))
        
        ads = result.get('ads', [])
        if ads:
            print(f"\n✅ 测试成功！共推荐了 {len(ads)} 个广告：")
            for ad in ads:
                print(f"   - [{ad['ad_id']}] {ad['title']} (匹配原因可能为: {ad['keywords']})")
        else:
            print("\n⚠️ 测试完成，但没有匹配到广告 (可能是LLM提取的关键词与库中不匹配，或代码逻辑问题)")
            
    except Exception as e:
        print(f"❌ 解析响应失败 (可能是服务端报错): {resp.text}")

if __name__ == "__main__":
    run_test()