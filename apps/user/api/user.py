from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from common.permissions import IsValidUser
from common.view.login_view import LoginModelViewSet
from user.filter.org_filter import OrgFilterClass
from user.models import User, Org
from user.serializers.user_serializers import UserSerializers, OrgSerializer


class OrgViewSet(LoginModelViewSet):
    queryset = Org.objects.all()
    permission_classes = [IsValidUser]
    serializer_class = OrgSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = OrgFilterClass
    search_fields = ['name']
    filterset_fields = ['name']
    ordering_fields = ['name', 'dept_id', 'level']


class UserViewSet(LoginModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsValidUser]
    serializer_class = UserSerializers
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['username', 'name', 'emp_no', 'dept__name']
    filterset_fields = ['role', 'account_type']
    ordering_fields = ['username']
