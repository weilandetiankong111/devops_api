import json
import os
import time

import xlrd
from django.shortcuts import render

from libs.aliyun_cloud import AliCloud
# from libs.aliyun_cloud import AliCloud
from libs.tencent_cloud import TCloud

from devops_api import settings
from system_config.models import Credential
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
# 序列化
from cmdb.models import Idc,ServerGroup,Server
from cmdb.serializers import IdcSerializer,ServerGroupSerializer,ServerSerializer
from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from libs.ssh import SSH
from django.http import FileResponse

# Create your views here.
class IdcViewSet(ModelViewSet):
    queryset = Idc.objects.all() # 指定操作的数据
    serializer_class = IdcSerializer # 指定序列化器
    filter_backends = [filters.SearchFilter,filters.OrderingFilter,DjangoFilterBackend] # 指定过滤器
    search_fields = ('name',)  # 指定可搜索字段
    filter_fields = ('city',)  # 指定过滤字段

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        res = {'code': 200, 'msg': '更新成功！'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除成功！'}
            return Response(res)
        except Exception as e:
            # return Response(status=status.HTTP_204_NO_CONTENT)
            res = {'code': 500, 'msg': '该IDC机房关联其他主机，请先删除关联的主机再操作！！'}
            return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        res = {'code': 200,'msg': '创建成功！'}
        return Response(res)

class ServerGroupViewSet(viewsets.ModelViewSet):
    queryset = ServerGroup.objects.all()
    serializer_class = ServerGroupSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name', )  # 指定可搜索字段
    filter_fields = ('city',)  # 指定过滤字段

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        hostname = request.data.get('hostname')

        # 一对多
        idc_id = int(request.data.get('idc'))
        idc_obj = Idc.objects.get(id=idc_id)
        server_obj = Server.objects.get(hostname=hostname)
        server_obj.idc = idc_obj
        server_obj.save()

        # 多对多
        group_id_list = request.data.get('server_group')
        server_obj.server_group.add(*group_id_list)

        res = {'code': 200, 'msg': '更新成功！'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除成功！'}
            return Response(res)
        except Exception as e:
            # return Response(status=status.HTTP_204_NO_CONTENT)
            res = {'code': 500, 'msg': '该分组关联其他主机，请先删除关联的主机再操作！！'}
            return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        res = {'code': 200,'msg': '该分组创建成功！'}
        return Response(res)

class ServerViewSet(ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name','hostname','public_ip','private_ip',)  # 指定可搜索字段
    filter_fields = ('idc','server_group',)  # 指定过滤字段

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        res = {'code': 200, 'msg': '更新成功！'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功！'}
        return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        res = {'code': 200,'msg': '主机创建成功！'}
        return Response(res)

class HostCollectView(APIView):
    def get(self,request):
        hostname = request.query_params.get('hostname')
        # ssh_ip = request.data.get('ssh_ip')
        # ssh_port = request.query_params['ssh_port']

        server = Server.objects.get(hostname=hostname)
        ssh_ip = server.ssh_ip
        ssh_port = server.ssh_port
        # credential_id = server.credential.id

        credential_id = request.query_params.get('credential_id')
        if not server.credential and not credential_id:
            result = {'code': 500, 'msg': '未发现凭据，请选择！'}
            return Response(result)
        elif server.credential:
            credential_id = int(server.credential.id)
        elif credential_id:
            credential_id = int(request.query_params.get('credential_id'))

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
        idc_id = int(request.data.get('idc'))  # 机房id
        print(request)
        print(request.data)
        print(idc_id)
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
            private_key = credential.private_key # key的内容，并不是一个文件
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

class ExcelCreateHostView(APIView):
    # 下载主机Excel模板
    def get(self,request):
        file_name = 'host.xlsx'
        file_path = os.path.join(settings.BASE_DIR, 'cmdb', 'file',file_name)
        response = FileResponse(open(file_path,'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment; filename=%s' %file_name
        return response
    # 导入
    def post(self,request):
        idc_id = int(request.data.get('idc')) # 机房id
        server_group_id_list = request.data.get('server_group')
        excel_file_obj = request.data['file']
        try:
            data = xlrd.open_workbook(file_contents=excel_file_obj.read())
        except Exception as e:
            res = {'code': 500, 'msg': '请上传excel文件'}
            return Response(res)

        table = data.sheets()[0]  # 打开第一个工作表
        nrows = table.nrows  #  获取表的行数

        idc = Idc.objects.get(id = idc_id)
        try:
            for i in range(nrows):  # 循环行
                if i != 0:  # 跳过标题行
                    name = table.row_values(i)[0]
                    hostname = table.row_values(i)[1]
                    ssh_ip = table.row_values(i)[2]
                    ssh_port = int(table.row_values(i)[3])
                    note = table.row_values(i)[4]

                    server = Server.objects.create(
                        idc = idc,
                        name = name,
                        hostname = hostname,
                        ssh_ip = ssh_ip,
                        ssh_port = ssh_port,
                        note = note
                     )
                    # 添加对对多字段
                    for group_id in server_group_id_list:
                        group = ServerGroup.objects.get(id=group_id)  # 根据id查询分组
                        server.server_group.add(group)  # 将服务器添加到分组
                res = {'code': 200,'msg': '导入成功'}
        except Exception as e:
            res = {'code': 500,'msg': '导入异常！%s' %e}
        return Response(res)

class AliyunCloudView(APIView):
    """
        阿里云获取云主机信息
        """

    # 获取地区(region)
    def get(self, request):
        secret_id = request.query_params.get('secret_id')
        secret_key = request.query_params.get('secret_key')

        cloud = AliCloud(secret_id, secret_key)
        result = cloud.region_list()

        if result['code'] == 200:
            data = []
            for r in result['data']['Regions']['Region']:
                rg = {'region_id': r['RegionId'], 'region_name': r['LocalName']}
                data.append(rg)
            res = {'code': 200, 'msg': '获取区域列表成功', 'data': data}
        else:
            res = {'code': 500, 'msg': result['msg']}

        return Response(res)

    # 导入云主机信息到数据库
    def post(self, request):
        secret_id = request.data.get('secret_id')
        secret_key = request.data.get('secret_key')
        server_group_id_list = request.data.get('server_group')
        region_id = request.data.get('region')  # 区域用于机房里的城市
        ssh_ip = request.data.get('ssh_ip')  # 用户选择使用内网（private）还是公网（public），下面判断对应录入
        ssh_port = int(request.data.get('ssh_port'))

        cloud = AliCloud(secret_id, secret_key)
        result = cloud.instance_list(region_id)

        if result['code'] == 200:
            instance_list = result['data']['Instances']['Instance']
            if len(instance_list) == 0:
                res = {'code': 500, 'msg': '该区域未发现云主机，请重新选择！'}
                return Response(res)
        else:
            res = {'code': 500, 'msg': '%s' % result['msg']}
            return Response(res)

        # 根据地区获取可用区
        zone_result = cloud.zone_list(region_id)
        zone_dict = {}  # {'cn-beijing-k': '华北 2 可用区 K'}
        for z in zone_result['data']['Zones']['Zone']:
            zone_dict[z['ZoneId']] = z['LocalName']

        # 根据云主机里zoneid获取对应的zone中文名
        zone_set = set()  # ('华北 2 可用区 K','华北 2 可用区 H')
        for host in instance_list:
            zone = host['ZoneId']
            zone_set.add(zone_dict[zone])

        # 根据可用区创建机房
        for zone in zone_set:
            # 如果机房不存在则创建
            idc = Idc.objects.filter(name=zone)
            if not idc:

                # 获取region的中文名
                region_list = cloud.region_list()['data']['Regions']['Region']
                for r in region_list:
                    if r['RegionId'] == region_id:
                        city = r['LocalName']

                Idc.objects.create(
                    name=zone,
                    city=city,
                    provider="阿里云"
                )

        for host in instance_list:
            instance_name = host['InstanceName']  # 机器名称
            hostname = host['HostName']  # 主机名
            instance_id = host['InstanceId']
            os_version = host['OSName']

            private_ip_list = host['NetworkInterfaces']['NetworkInterface'][0]['PrivateIpSets']['PrivateIpSet']
            private_ip = []
            for ip in private_ip_list:
                private_ip.append(ip['PrivateIpAddress'])

            public_ip = host['PublicIpAddress']['IpAddress']
            cpu = "%s核" % host['Cpu']
            memory = "%sG" % (int(host['Memory']) / 1024)

            # 硬盘信息需要单独获取
            disk = []
            disk_list = cloud.instance_disk(instance_id)['data']['Disks']['Disk']
            for d in disk_list:
                disk.append({'device': d['Device'], 'size': '%sG' % d['Size'], 'type': None})

            create_date = time.strftime("%Y-%m-%d", time.strptime(host['CreationTime'], "%Y-%m-%dT%H:%MZ"))
            # 2022-01-30T04:51Z 需要转换才能存储
            expired_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(host['ExpiredTime'], "%Y-%m-%dT%H:%MZ"))

            if ssh_ip == "public":
                ssh_ip = public_ip[0]
            elif ssh_ip == "private":
                ssh_ip = private_ip[0]

            server = Server.objects.filter(hostname=instance_id)
            if not server:
                zone = host['ZoneId']
                idc_name = zone_dict[zone]
                idc = Idc.objects.get(name=idc_name)

                server = Server.objects.create(
                    idc=idc,
                    name=instance_name,
                    hostname=instance_id,
                    ssh_ip=ssh_ip,
                    ssh_port=ssh_port,
                    machine_type='cloud_vm',
                    os_version=os_version,
                    public_ip=public_ip,
                    private_ip=private_ip,
                    cpu_num=cpu,
                    memory=memory,
                    disk=disk,
                    put_shelves_date=create_date,
                    expire_datetime=expired_time,
                    is_verified='verified'
                )
                # 添加多对多字段
                for group_id in server_group_id_list:
                    group = ServerGroup.objects.get(id=group_id)  # 获取分组
                    server.server_group.add(group)  # 将服务器添加到分组
            else:
                print("该云主机已经存在！")

        res = {'code': 200, 'msg': '导入云主机成功'}
        return Response(res)

class TencentCloudView(APIView):
    # 获取地区(region)
    def get(self, request):
        secret_id = request.query_params.get('secret_id')
        secret_key = request.query_params.get('secret_key')

        cloud = TCloud(secret_id, secret_key)
        result = cloud.region_list()

        if result.code == 200:
            data = []
            for r in result.RegionSet:
                rg = {'region_id': r.Region, 'region_name': r.RegionName}
                data.append(rg)
            res = {'code': 200, 'msg': '获取区域列表成功', 'data': data}
        else:
            res = {'code': 500, 'msg': result['msg']}

        return Response(res)

    # 导入云主机信息到数据库
    def post(self, request):
        secret_id = request.data.get('secret_id')
        secret_key = request.data.get('secret_key')
        server_group_id_list = request.data.get('server_group')
        region_id = request.data.get('region')  # 区域用于机房里的城市
        ssh_ip = request.data.get('ssh_ip')  # 用户选择使用内网（private）还是公网（public），下面判断对应录入
        ssh_port = int(request.data.get('ssh_port'))

        cloud = TCloud(secret_id, secret_key)
        result = cloud.instance_list(region_id)

        if result.code == 200:
            instance_list = result.InstanceSet
            if len(instance_list) == 0:
                res = {'code': 500, 'msg': '该区域未发现云主机，请重新选择！'}
                return Response(res)
        else:
            res = {'code': 500, 'msg': '%s' % result['msg']}
            return Response(res)

        # 根据地区获取可用区
        zone_result = cloud.zone_list(region_id)
        zone_dict = {}  # {'cn-beijing-k': '华北 2 可用区 K'}
        for z in zone_result.ZoneSet:
            zone_dict[z.Zone] = z.ZoneName

        # 根据云主机里zoneid获取对应的zone中文名
        zone_set = set()  # ('华北 2 可用区 K','华北 2 可用区 H')
        for host in instance_list:
            zone = host.Placement.Zone
            zone_set.add(zone_dict[zone])

        # 根据可用区创建机房
        for zone in zone_set:
            # 如果机房不存在则创建
            idc = Idc.objects.filter(name=zone)
            if not idc:

                # 获取region的中文名
                region_list = cloud.region_list().RegionSet
                for r in region_list:
                    if r.Region == region_id:
                        city = r.RegionName

                Idc.objects.create(
                    name=zone,
                    city=city,
                    provider="腾讯云"
                )

        for host in instance_list:
            instance_id = host.InstanceId  # 实例ID
            instance_name = host.InstanceName # 机器名称

            os_version = host.OsName
            private_ip = host.PrivateIpAddresses
            public_ip = host.PublicIpAddresses
            cpu = "%s核" %host.CPU
            memory = "%sG" %host.Memory

            disk = [{'device': 'None', 'size': host.SystemDisk.DiskSize, 'type': 'None'}]  # 默认保存是系统盘
            data_list = host.DataDisks
            if data_list:
                for d in data_list:
                    disk.append({'device': 'None', 'size': d.DiskSize, 'type': 'None'})

            create_date = time.strftime("%Y-%m-%d", time.strptime(host.CreatedTime, "%Y-%m-%dT%H:%M:%SZ"))
            # 2022-01-30T04:51Z 需要转换才能存储
            expired_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(host.ExpiredTime, "%Y-%m-%dT%H:%M:%SZ"))

            if ssh_ip == "public":
                ssh_ip = public_ip[0]
            elif ssh_ip == "private":
                ssh_ip = private_ip[0]

            server = Server.objects.filter(hostname=instance_id)
            if not server:
                zone = host.Placement.Zone
                idc_name = zone_dict[zone]
                idc = Idc.objects.get(name=idc_name)

                server = Server.objects.create(
                    idc=idc,
                    name=instance_name,
                    hostname=instance_id,
                    ssh_ip=ssh_ip,
                    ssh_port=ssh_port,
                    machine_type='cloud_vm',
                    os_version=os_version,
                    public_ip=public_ip,
                    private_ip=private_ip,
                    cpu_num=cpu,
                    memory=memory,
                    disk=disk,
                    put_shelves_date=create_date,
                    expire_datetime=expired_time,
                    is_verified='verified'
                )
                # 添加多对多字段
                for group_id in server_group_id_list:
                    group = ServerGroup.objects.get(id=group_id)  # 获取分组
                    server.server_group.add(group)  # 将服务器添加到分组
            else:
                print("该云主机已经存在！")

        res = {'code': 200, 'msg': '导入云主机成功'}
        return Response(res)