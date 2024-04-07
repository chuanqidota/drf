from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from common.minxins.ExportMinxin import ExportMix
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


class UserViewSet(LoginModelViewSet, ExportMix):
    queryset = User.objects.all()
    permission_classes = [IsValidUser]
    serializer_class = UserSerializers
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['username', 'name', 'emp_no', 'dept__name']
    filterset_fields = ['role', 'account_type']
    ordering_fields = ['username']

    file_name = "user"
    xlsx_header_to_fields = {
        "dept_name": '部门名称',
        "username": "用户名",
        "name": "名称",
        "emp_no": "唯一标号",
        "is_active_display": "是否可用",
        "role_display": "角色",
        "account_display": "账户类型"
    }

    def list(self, request, *args, **kwargs):
        if self.request.query_params.get("export", None) == "true":
            return self.response_xlsx()
        return super().list(request, *args, **kwargs)
