from system_config.models import Credential
from app_release.models import Notify
from rest_framework import serializers

class CredentialSerializer(serializers.ModelSerializer):
    """
    凭据序列化类
    """
    class Meta:
        model = Credential
        fields = "__all__"
        read_only_fields = ('id',)

class NotifySerializer(serializers.ModelSerializer):
    """
    消息通知序列化类
    """
    class Meta:
        model = Notify
        fields = "__all__"
        read_only_fields = ('id',)