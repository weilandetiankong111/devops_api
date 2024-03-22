import json
import os

from django.shortcuts import render

from devops_api import settings
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

class CreateHostView(APIView):
    def post(self,request):
        idc_id = int(request.data.get('idc_id'))
        server_group_id_list = request.data.get('server_group')
        name = request.data.get('name')
        hostname = request.data.get('hostname')
        print(hostname)
        ssh_ip = request.data.get('ssh_ip')
        ssh_port = int(request.data.get('ssh_port'))
        credential_id = int(request.data.get('credential'))
        note = request.data.get('note')
        # 如果主机存在返回
        server = Server.objects.filter(hostname=hostname)
        if server:
            result = {'code': 500, 'msg': '主机已存在！'}
            return Response(result)

        # 通过凭据ID获取用户名信息
        credential = Credential.objects.get(id=credential_id)
        username = credential.username
        if  credential.auth_mode == 1:
            password = credential.password
            ssh =SSH(ssh_ip, ssh_port, username, password=password)
        else:
            private_key = credential.private_key
            ssh = SSH(ssh_ip, ssh_port,username, key=private_key)

        test = ssh.test()  # 测试SSH连接通过
        if test['code'] == 200:
            client_agent_name = "host_collect.py"
            local_file = os.path.join(settings.BASE_DIR, 'cmdb', 'file', client_agent_name)
            remote_file = os.path.join(settings.CLIENT_COLLECT_DIR, client_agent_name)  # 这个工作路径在setting里配置
            ssh.scp(local_file, remote_file=remote_file)
            ssh.command('chmod +x %s' % remote_file)
            result = ssh.command('python %s' % remote_file)

            if result['code'] == 200:  # 采集脚本执行成功
                data = json.loads(result['data'])
                print(hostname)
                print(data['hostname'])
                if hostname != data['hostname']:
                    result = {'code': 500, 'msg': '填写的主机名与目标主机不一致，请核对后再提交！'}
                    return Response(result)

                # 1.基本主机信息入库（人工录入）
                idc = Idc.objects.get(id=idc_id)  # 根据id查询IDC
                server_obj = Server.objects.create(
                    idc=idc,
                    name=name if name else hostname,
                    hostname=hostname,
                    ssh_ip=ssh_ip,
                    ssh_port=ssh_port,
                    is_verified='verified',
                    credential=credential,
                    note=note
                )
                # 添加对对多字段
                for group_id in server_group_id_list:
                    group = ServerGroup.objects.get(id=group_id)  # 根据id查询分组
                    server_obj.server_group.add(group)  # 将服务器添加到分组

                # 2.主机配置入库（自动采集）
                server.update(**data)
                result = {'code': 200, 'msg': '添加主机成功并同步配置'}
            else:
                result = {'code': 500, 'msg': '采集主机配置失败！错误：%s' % result['msg']}
        else:
            result = {'code': 500, 'msg': 'SSH连接异常！错误：%s' % test['msg']}

        return Response(result)