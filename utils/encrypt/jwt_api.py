# PyJWT==WT-2.10.1
import secrets

import jwt
import datetime
import uuid
from jwt import ExpiredSignatureError, InvalidTokenError


def generate_api_key() -> str:
    """生成API密钥

    Returns:
        生成的API密钥
    """
    return secrets.token_urlsafe(32)


class JWTManager:
    def __init__(self, secret_key, algorithm="HS256", access_expires=1800, refresh_expires=604800):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expires = access_expires
        self.refresh_expires = refresh_expires

    def _generate_token(self, user_id, token_type, expires_seconds, jti=None):
        now = datetime.datetime.utcnow()
        payload = {
            "sub": str(user_id),
            "type": token_type,  # access / refresh
            "iat": now,
            "exp": now + datetime.timedelta(seconds=expires_seconds),
            "jti": jti or uuid.uuid4().hex  # token唯一ID
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_access_token(self, user_id):
        """
            生成access token
        :param user_id:
        :return:
        """
        return self._generate_token(user_id, "access", self.access_expires)

    def generate_refresh_token(self, user_id):
        """
            生产refresh token
        :param user_id:
        :return:
        """
        jti = uuid.uuid4().hex
        token = self._generate_token(user_id, "refresh", self.refresh_expires, jti)
        return token, jti

    def decode_token(self, token):
        """
            解密token
        :param token:
        :return:
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            return {"error": "token_expired"}
        except InvalidTokenError:
            return {"error": "invalid_token"}


if __name__ == '__main__':
    secret_key = generate_api_key()
    jwt_manager = JWTManager(secret_key=secret_key)

    cache = None


    def login_user(user):
        """
            用户登陆
        :param user:
        :return:
        """
        access_token = jwt_manager.generate_access_token(user.id)
        refresh_token, jti = jwt_manager.generate_refresh_token(user.id)

        # 存 refresh token 到 Redis
        cache.set(f"refresh_token:{jti}", user.id, timeout=7 * 24 * 3600)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }


    def refresh_access_token(refresh_token):
        """
            刷新access_token
        :param refresh_token:
        :return:
        """
        payload = jwt_manager.decode_token(refresh_token)
        if "error" in payload:
            return None, "refresh token invalid"

        if payload["type"] != "refresh":
            return None, "wrong token type"

        jti = payload["jti"]
        user_id = cache.get(f"refresh_token:{jti}")

        if not user_id:
            return None, "refresh token revoked"

        new_access_token = jwt_manager.generate_access_token(user_id)
        return new_access_token, None


    def logout(refresh_token):
        payload = jwt_manager.decode_token(refresh_token)
        if "jti" in payload:
            cache.delete(f"refresh_token:{payload['jti']}")
"""
登录:
  发 access(30min) + refresh(7d)
        ↓
访问接口:
  校验 access token
        ↓
access 过期:
  用 refresh 换新 access （通过jti换user_id）
        ↓
退出登录 / 管理员踢人:
  删除 Redis 中 refresh token
        ↓
refresh 失效 → 无法再生成 access → 强制下线
"""
