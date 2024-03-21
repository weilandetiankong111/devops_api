from django.shortcuts import render
from system_config.models import Credential
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
# 序列化
from cmdb.models import Idc,ServerGroup,Server
from cmdb.serializers import IdcSerializer,ServerGroupSerializer,ServerSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from libs.ssh import SSH


# Create your views here.
class IdcViewSet(ModelViewSet):
    queryset = Idc.objects.all()
    serializer_class = IdcSerializer
    filter_backends = [filters.SearchFilter,filters.OrderingFilter,DjangoFilterBackend] # 指定过滤器
    search_fields = ['name',]  # 指定可搜索字段
    filterset_fields = ('city',)  # 指定过滤字段

class ServerGroupViewSet(ModelViewSet):
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ['name', ]  # 指定可搜索字段
    filterset_fields = ('name',)  # 指定过滤字段

class ServerViewSet(ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ['name','hostname','public_ip','private_ip', ]  # 指定可搜索字段
    filterset_fields = ('idc','server_group',)  # 指定过滤字段

class HostCollectView(APIView):
    def get(self,request):
        hostname = request.query_params.get('hostname')
        # ssh_ip = request.data.get('ssh_ip')
        # ssh_port = request.query_params['ssh_port']

        server = Server.objects.get(hostname=hostname)
        ssh_ip = server.ssh_ip
        ssh_port = server.ssh_port
        credential_id = server.credential.id
        print(ssh_ip,ssh_port,credential_id)

        # 通过凭据ID获取SSH用户名和密码
        credential = Credential.objects.get(id=credential_id)
        username = credential.username
        if credential.auth_mode == 1:
            password = credential.password
            ssh = SSH(ssh_ip, ssh_port, username, password=password)
        else:
            private_key = credential.private_key  # key的内容，并不是一个文件
            ssh = SSH(ssh_ip, ssh_port, username, key=private_key)

        result = ssh.command('ls -l /etc')
        print(result)
        return Response(result)
