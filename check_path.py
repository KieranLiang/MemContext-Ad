# -*- coding: utf-8 -*-
import os
import json

# 配置文件路径
config_path = r'c:\Users\tianhaoxuan\Desktop\MemContext-Ad\memcontext-mcp\config.json'

# 读取配置
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 解析路径（按照 server_new.py 的逻辑）
config_dir = os.path.dirname(os.path.abspath(config_path))
data_storage_path = config['data_storage_path']

print("=" * 60)
print("MCP 配置检查")
print("=" * 60)
print(f"\n配置文件路径: {config_path}")
print(f"配置文件所在目录: {config_dir}")
print(f"\n配置中的 data_storage_path: {data_storage_path}")

if not os.path.isabs(data_storage_path):
    # 相对路径解析
    resolved_path = os.path.join(config_dir, data_storage_path)
    resolved_path = os.path.normpath(resolved_path)
    print(f"\n解析后的绝对路径: {resolved_path}")
    print(f"路径是否存在: {os.path.exists(resolved_path)}")
    
    # 检查用户目录
    users_dir = os.path.join(resolved_path, "users")
    print(f"\n用户数据目录: {users_dir}")
    print(f"用户数据目录是否存在: {os.path.exists(users_dir)}")
    
    if os.path.exists(users_dir):
        users = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
        print(f"现有用户: {users}")
        
        # 检查 test_user_001 的短期记忆
        user_001_dir = os.path.join(users_dir, "test_user_001")
        short_term_file = os.path.join(user_001_dir, "short_term.json")
        if os.path.exists(short_term_file):
            print(f"\ntest_user_001 的短期记忆文件存在: {short_term_file}")
            with open(short_term_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"短期记忆条数: {len(data)}")
else:
    print(f"\n绝对路径: {data_storage_path}")
    print(f"路径是否存在: {os.path.exists(data_storage_path)}")

print("\n" + "=" * 60)
