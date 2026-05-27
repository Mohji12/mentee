import redis

redis_client = redis.StrictRedis(
    host='merry-skunk-15104.upstash.io',
    port=6379,
    username='default',
    password='ATsAAAIjcDE0YWZlYjM5ZmE4Yjk0NzRjYTVmNzU2Mjg2ODFjMGVhMHAxMA',  # Replace with your actual password
    ssl=True,  # Use SSL/TLS
    decode_responses=True)