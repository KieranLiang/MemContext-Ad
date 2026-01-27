import redis
r = redis.from_url("redis://localhost:6379/0")
print(r.ping() ) # 返回 True 表示连通

