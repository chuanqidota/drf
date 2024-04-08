from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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
        # 排除字段
        exclude = ['_password']
        # 联合唯一
        validators = [ 
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'name'] 
            )
        ]

    # 指定字段的校验方式
    def validate_username(self, value):
        if len(value)<4:
            raise serializers.ValidationError("用户名长度不能低于4")
        return value
    
    # 不指定字段的校验方式
    def validate(self, data):
        if len(data['username']) > 10:
            raise serializers.ValidationError("用户名长度不能超过10")
        return data
