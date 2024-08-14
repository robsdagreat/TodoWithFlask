from flask import request, jsonify
from functools import wraps
import time
from app import cache

def throttle(limit=100, per=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = f"{request.remote_addr}:{request.endpoint}"
            current = time.time()
            count, start = cache.get(key) or (0, current)
            
            if current - start > per:
                count = 0
                start = current
            
            if count >= limit:
                return jsonify({"error": "Too many requests"}), 429
            
            cache.set(key, (count + 1, start), timeout=per)
            return f(*args, **kwargs)
        return wrapped
    return decorator