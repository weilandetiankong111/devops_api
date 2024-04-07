from rest_framework.viewsets import ModelViewSet
from app_release.models import Env, Project, App, ReleaseConfig, ReleaseApply,HistoryVersion
from system_config.models import Notify
from app_release.serializers import EnvSerializer, ProjectSerializer, AppSerializer, ReleaseConfigSerializer,ReleaseApplySerializer

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from rest_framework.response import Response
from django.conf import settings

from system_config.models import Credential
from libs.gitlib import Git, git_repo_auth
import os
from datetime import datetime

from libs.ansible_cicd import AnsibleApi
from cmdb.models import Server
from libs.dingding import dingtalk_msg

class EnvViewSet(ModelViewSet):
    queryset = Env.objects.all()  # 指定操作的数据
    serializer_class = EnvSerializer  # 指定序列化器

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name','english_name')  # 指定可搜索的字段

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        res = {'code': 200, 'msg': '更新成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除成功'}
            return Response(res)
        except Exception as e:
            res = {'code': 500, 'msg': '该环境关联其他发布配置，请先删除关联的发布配置再操作！'}
            return Response(res)

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('name','english_name')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        res = {'code': 200, 'msg': '更新成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除成功'}
            return Response(res)
        except Exception as e:
            res = {'code': 500, 'msg': '该项目关联其他应用，请先删除关联的应用再操作！'}
            return Response(res)

class AppViewSet(ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name','english_name')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)

        # 一对多
        project = request.data.get('project')
        project_obj = Project.objects.get(id=project)
        App.objects.create(
            name=request.data.get('name'),
            english_name=request.data.get('english_name'),
            project=project_obj
        )

        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)

        # 处理一对多关系
        project = request.data.get('project')
        project_obj = Project.objects.get(id=project)
        del request.data['project']
        App.objects.filter(
            id=pk
        ).update(
            project=project_obj,
            **request.data
        )

        res = {'code': 200, 'msg': '更新成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功'}
        return Response(res)

class ReleaseConfigViewSet(ModelViewSet):
    queryset = ReleaseConfig.objects.all()
    serializer_class = ReleaseConfigSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name','english_name')

    # 指定自定义的过滤器
    from .serializers import ReleaseConfigFilter
    filterset_class = ReleaseConfigFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        res = {'code': 200, 'msg': '创建成功', 'data': serializer.data}
        return Response(res)

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)

        # 一对多
        app = request.data.get('app')
        env = request.data.get('env')
        app_obj = App.objects.get(id=app)
        env_obj = Env.objects.get(id=env)
        del request.data['app']
        del request.data['env']
        ReleaseConfig.objects.create(
            app=app_obj,
            env=env_obj,
            **request.data
        )
        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)

        app = request.data.get('app')
        env = request.data.get('env')
        app_obj = App.objects.get(id=app)
        env_obj = Env.objects.get(id=env)

        del request.data['app']
        del request.data['env']

        ReleaseConfig.objects.filter(
            id=pk
        ).update(
            app=app_obj,
            env=env_obj,
            **request.data
        )

        res = {'code': 200, 'msg': '更新成功'}
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            res = {'code': 200, 'msg': '删除成功'}
            return Response(res)
        except Exception as e:
            res = {'code': 500, 'msg': '该发布配置关联其他发布申请，请先删除关联的发布申请再操作！'}
            return Response(res)

class ReleaseApplyViewSet(ModelViewSet):
    queryset = ReleaseApply.objects.all()
    serializer_class = ReleaseApplySerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('name','english_name')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        res = {'code': 200, 'msg': '获取成功', 'data': serializer.data}
        return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)

        release_config = request.data.get('release_config_id')
        del request.data['release_config_id']
        del request.data['env']
        del request.data['app']
        config_obj = ReleaseConfig.objects.get(id=release_config)
        ReleaseApply.objects.create(
            release_config=config_obj,
            **request.data
        )

        res = {'code': 200, 'msg': '创建成功'}
        return Response(res)

    # def update(self, request, pk=None, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     # self.perform_update(serializer)
    #
    #     release_config = request.data.get('release_config')
    #     config_obj = ReleaseConfig.objects.get(id=release_config)
    #     del request.data['release_config']
    #     ReleaseApply.objects.filter(
    #         id=pk
    #     ).update(
    #         release_config=config_obj,
    #         **request.data
    #     )
    #     res = {'code': 200, 'msg': '更新成功'}
    #     return Response(res)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        res = {'code': 200, 'msg': '删除成功'}
        return Response(res)

class GitView(APIView):
    def get(self, request):
        git_repo = request.query_params.get('git_repo')
        git_credential_id = int(request.query_params.get('git_credential_id'))
        git = Git(git_repo, os.path.join(settings.BASE_DIR, "repos"))
        # git没凭据
        if git_credential_id == 0:
            git.get_repo()
            branch = git.get_branch()
            res = {'code': 200, 'msg': '获取成功', 'data': branch}
            return Response(res)
        else:
            cred_obj = Credential.objects.get(id=git_credential_id)
            username = cred_obj.username
            password = cred_obj.password
            git_repo = git_repo_auth(git_repo,username,password)
            git = Git(git_repo, os.path.join(settings.BASE_DIR, "repos"))
            git.get_repo()
            branch = git.get_branch()
            res = {'code': 200, 'msg': '获取成功', 'data': branch}
            return Response(res)

class DeployView(APIView):
    def post(self, request):
        print(request.data)

        # 发布申请相关信息
        apply_id = int(request.data.get('id'))
        branch = request.data.get('branch')
        server_ids = request.data.get('server_ids')

        # 发布配置相关信息
        release_config = request.data.get('release_config')
        git_repo = release_config['git_repo']
        source_file = release_config['source_file']
        pre_checkout_script = release_config['pre_checkout_script']
        post_checkout_script = release_config['post_checkout_script']
        dst_dir = release_config['dst_dir']
        history_version_dir = release_config['history_version_dir']
        history_version_number = release_config['history_version_number']
        pre_deploy_script = release_config['pre_deploy_script']
        post_deploy_script = release_config['post_deploy_script']
        notify_id = release_config['notify_id']
        note = release_config['note']

        app_name = release_config['app']['english_name']
        # 版本标识：项目名称-应用名称-时间
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        version_id = "%s-%s-%s" %(release_config['app']['project']['english_name'], release_config['app']['english_name'], timestamp)

        # 将脚本写入文件
        with open('/tmp/pre_checkout_script.sh', 'w') as f:
            f.write(pre_checkout_script)
        with open('/tmp/post_checkout_script.sh', 'w') as f:
            f.write(post_checkout_script)
        with open('/tmp/pre_deploy_script.sh', 'w') as f:
            f.write(pre_deploy_script)
        with open('/tmp/post_deploy_script.sh', 'w') as f:
            f.write(post_deploy_script)

        git_credential_id = release_config['git_credential_id']
        if git_credential_id != 0:
            credential = Credential.objects.get(id=git_credential_id)
            git_repo = git_repo_auth(git_repo, credential.username, credential.password)

        ansible = AnsibleApi()
        # 将发布配置部分变量传递给playbook使用
        extra_vars = {
            "git_repo": git_repo,
            "branch": branch,
            "dst_dir": dst_dir,
            "history_version_dir": history_version_dir,
            "history_version_number": history_version_number,
            "app_name": app_name,
            "version_id": version_id,
            "source_file": source_file
        }
        ansible.variable_manager._extra_vars = extra_vars

        # 创建一个分组
        ansible.inventory.add_group("webservers")
        for i in server_ids:
            server_obj = Server.objects.get(id=i)
            # ssh_ip、ssh_port、ssh用户名、ssh密码
            ssh_ip = server_obj.ssh_ip
            ssh_port = server_obj.ssh_port
            if server_obj.credential:
                ssh_user = server_obj.credential.username
                if server_obj.credential.auth_mode == 1:
                    ssh_pass = server_obj.credential.password
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_pass', value=ssh_pass)
                else:
                    ssh_key = server_obj.credential.private_key
                    key_file = "/tmp/.ssh_key"
                    with open(key_file, 'w') as f:
                        f.write(ssh_key)
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_private_key_file', value=key_file)
            else:
                ssh_user = 'root'
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_port', value=ssh_port)
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_user', value=ssh_user)
            # 向组内添加主机
            ansible.inventory.add_host(host=ssh_ip,group="webservers")

        playbook = os.path.join(settings.BASE_DIR, 'app_release/files/deploy.yaml')
        status = ansible.playbook_run([playbook]) # 返回一个状态码，0是正常，非0是有任务异常
        result = ansible.get_result()

        def notify(content):
            from system_config.models import Notify
            notify_obj = Notify.objects.get(id=notify_id)
            if notify_obj.notify_mode == 1:
                pass
            elif notify_obj.notify_mode == 2:
                webhook = notify_obj.dingding_webhook
                dingtalk_msg(webhook, content)
            elif notify_obj.notify_mode == 3:
                pass

        if status == 0:
            ReleaseApply.objects.filter(id=apply_id).update(status=3, deploy_result=result)
            notify("通知：%s, 发布成功" %version_id)
            res = {'code': 200, 'msg': '发布成功', 'data': result}
        else:
            ReleaseApply.objects.filter(id=apply_id).update(status=4, deploy_result=result)
            notify("通知：%s, 发布失败！" % version_id)
            res = {'code': 500, 'msg': '发布异常！', 'data': result}
            return Response(res)

        # 记录发布版本
        project_id= int(release_config['app']['project']['id'])
        env_id = int(release_config['env']['id'])
        app_id = int(release_config['app']['id'])
        title = request.data.get('title')

        HistoryVersion.objects.create(
            project_id=project_id,
            env_id=env_id,
            app_id=app_id,
            title=title,
            server_ids=server_ids,
            version_id=version_id,
            note=note,
        )

        return Response(res)

class RollbackView(APIView):
    def get(self, request):
        project_id = int(request.query_params.get('project_id'))
        env_id = int(request.query_params.get('env_id'))
        app_id = int(request.query_params.get('app_id'))

        queryset_obj = HistoryVersion.objects.filter(project_id=project_id, env_id=env_id, app_id=app_id)
        if queryset_obj:
            data = [] # [{},{},{}]
            for i in queryset_obj:
                d = {'id': i.id, 'title': i.title, 'version_id': i.version_id,
                     'server_ids': i.server_ids, 'release_time': i.release_time,
                     'note': i.note}
                data.append(d)
            res = {'code': 200, 'msg': '获取成功', 'data': data}
        else:
            res = {'code': 500, 'msg': '没有发布记录！'}

        return Response(res)

    def post(self, request):
        dst_dir = request.data.get('dst_dir')
        history_version_dir = request.data.get('history_version_dir')
        apply_id = request.data.get('apply_id')
        version_id = request.data.get('version_id')
        server_ids = request.data.get('server_ids')
        post_rollback_script = request.data.get('post_rollback_script')

        with open('/tmp/post_rollback_script.sh', 'w') as f:
            f.write(post_rollback_script)

        ansible = AnsibleApi()
        # 将发布配置部分变量传递给playbook使用
        extra_vars = {
            "dst_dir": dst_dir,
            "history_version_dir": history_version_dir,
            "version_id": version_id,
        }
        ansible.variable_manager._extra_vars = extra_vars

        # 创建一个分组
        ansible.inventory.add_group("webservers")
        for i in server_ids:
            server_obj = Server.objects.get(id=i)
            # ssh_ip、ssh_port、ssh用户名、ssh密码
            ssh_ip = server_obj.ssh_ip
            ssh_port = server_obj.ssh_port
            if server_obj.credential:
                ssh_user = server_obj.credential.username
                if server_obj.credential.auth_mode == 1:
                    ssh_pass = server_obj.credential.password
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_pass', value=ssh_pass)
                else:
                    ssh_key = server_obj.credential.private_key
                    key_file = "/tmp/.ssh_key"
                    with open(key_file, 'w') as f:
                        f.write(ssh_key)
                    ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_private_key_file',
                                                               value=key_file)
            else:
                ssh_user = 'root'
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_port', value=ssh_port)
            ansible.variable_manager.set_host_variable(host=ssh_ip, varname='ansible_ssh_user', value=ssh_user)
            # 向组内添加主机
            ansible.inventory.add_host(host=ssh_ip, group="webservers")

        playbook = os.path.join(settings.BASE_DIR, 'app_release/files/rollback.yaml')
        status = ansible.playbook_run([playbook]) # 返回一个状态码，0是正常，非0是有任务异常
        result = ansible.get_result()
        print(result)

        if status == 0:
            res = {'code': 200, 'msg': '回滚成功'}
        else:
            for task in result:
                if result[task]['failed']:
                    for ip in result[task]['failed']:
                        error = result[task]['failed'][ip]['stderr']
                elif result[task]['unreachable']:
                    for ip in result[task]['unreachable']:
                        error = result[task]['failed'][ip]['msg']
            res = {'code': 500, 'msg': '回滚异常！', 'data': error}
        return Response(res)

class ApplyEchartView(APIView):
    """
    数据格式：
    # X: ['2022-7-11', '2022-7-12', '2022-7-13', '2022-7-14', '2022-7-15', '2022-7-16', '2022-7-16']
    # Y1:  [1, 3, 5, 6, 2, 1, 3]
    # Y2:  [3, 21, 4, 2, 1, 3, 2]
    """
    def get(self,request):
        from datetime import datetime, timedelta
        import pandas as pd

        end = datetime.now()
        start = (end - timedelta(30))
        queryset_obj = ReleaseApply.objects.filter(
            release_time__range=[start, end])  # 或者大于小于 filter(deal_date__gte=week, deal_date__lte=cur_date)

        # 生成时间序列
        date_range = pd.date_range(start=datetime.strftime(start, "%Y-%m-%d"),
                                   end=datetime.strftime(end, "%Y-%m-%d"))  # datetime时间转为日期

        x_data = []
        y_fail_data = []
        y_success_data = []

        for date in date_range:
            date = datetime.strftime(date, "%Y-%m-%d")
            x_data.append(date)
            y_fail_n = 0
            y_success_n = 0
            for i in queryset_obj:
                date_time = datetime.strftime(i.release_time, "%Y-%m-%d")
                if date == date_time:
                    if i.status == 3:  # 3 发布成功
                        y_success_n += 1
                    elif i.status == 4:  # 4 发布失败
                        y_fail_n += 1
            y_fail_data.append(y_fail_n)
            y_success_data.append(y_success_n)

        data = {'y_fail_data': y_fail_data, 'y_success_data': y_success_data, 'x_data': x_data}
        res = {'data': data, 'code': 200, 'msg': '成功'}
        return Response(res)

