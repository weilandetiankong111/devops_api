from cmdb.models import Idc,ServerGroup,Server
from rest_framework import serializers

class IdcSerializer(serializers.ModelSerializer):
    """
    IDC机房序列化类
    """
    class Meta:
        model = Idc
        fields = "__all__"
        read_only_fields = ("id",)  # 仅用于序列化（只读）字段，反序列化（更新）可不传

class ServerGroupSerializer(serializers.ModelSerializer):
    """
    主机分组序列化类
    """
    class Meta:
        model = ServerGroup
        fields = "__all__"
        read_only_fields = ("id",)

class ServerSerializer(serializers.ModelSerializer):
    """
    服务器序列化类
    """
    # idc = IdcSerializer() # 一对多
    class Meta:
        model = Server
        fields = "__all__"
        read_only_fields = ("id",)