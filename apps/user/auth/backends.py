from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UserPassWordAuthBackend(ModelBackend):
    """
        登录认证回调
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            return None
        if user.check_password(password):
            return user
        else:
            return None

