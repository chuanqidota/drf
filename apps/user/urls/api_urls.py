from django.urls import path
from rest_framework.routers import DefaultRouter

from user.api.login import LoginView, LogoutView, ManualLoginView

router = DefaultRouter()
urlpatterns = [
    path('v1/login/', LoginView.as_view(), name='login'),
    path('v1/logout/', LogoutView.as_view(), name='logout'),
    path('v1/manual-login/', ManualLoginView.as_view(), name='manual-login'),
]

urlpatterns += router.urls
