import os
import jwt  # Make sure to install PyJWT or similar library
import time
from src.config.config import app_config
import traceback

def verify_api_key(api_key: str) -> bool:
    return api_key == os.getenv('ADMIN_API_KEY')

# return token and expiresAt (as unix timestamp)
def generate_jwt() -> (str, int):
    # Implement JWT generation logic here
    # Example: payload = {'some': 'data'}
    # return jwt.encode(payload, 'your-secret-key', algorithm='HS256')
    payload = {'exp': time.time() + app_config.admin.jwt_expiration}  # Token expires in 1 hour
    return jwt.encode(payload, app_config.admin.jwt_secret, algorithm='HS256'), payload['exp']

def verify_jwt(token: str) -> bool:
    try:
        payload = jwt.decode(token, app_config.admin.jwt_secret, algorithms=['HS256'])
        return payload['exp'] > time.time()
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    except Exception as e:
        traceback.print_exc()
        return False
