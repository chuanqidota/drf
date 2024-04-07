from rest_framework import serializers

from user.models import User, Org


class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Org
        fields = '__all__'


class UserSerializers(serializers.ModelSerializer):
    org = OrgSerializer(read_only=True)
    dept_name = serializers.ReadOnlyField(help_text='部门')
    role_display = serializers.ReadOnlyField(help_text='角色')
    account_display = serializers.ReadOnlyField(help_text='账户')
    is_active_display = serializers.ReadOnlyField(help_text='是否可用')

    class Meta:
        model = User
        exclude = ['_password']
