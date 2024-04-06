from rest_framework import serializers

from user.models import User, Org


class OrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Org
        fields = '__all__'


class UserSerializers(serializers.ModelSerializer):
    org = OrgSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ['_password']
