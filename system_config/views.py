from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from system_config.serializers import CredentialSerializer
from system_config.models import Credential

class CredentialViewSet(ModelViewSet):
    queryset = Credential.objects.all()  # 指定操作的数据
    serializer_class = CredentialSerializer  # 指定序列化器