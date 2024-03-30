from rest_framework.viewsets import ModelViewSet
from system_config.models import Credential, Notify
from system_config.serializers import CredentialSerializer, NotifySerializer
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

class CredentialViewSet(ModelViewSet):
    queryset = Credential.objects.all()  # 指定操作的数据
    serializer_class = CredentialSerializer  # 指定序列化器

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name', )  # 指定可搜索的字段
    # filter_fields = ('name',)   # 指定过滤的字段

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
            res = {'code': 500, 'msg': '该凭据关联其他主机，请先删除关联的主机再操作！'}
            return Response(res)

class NotifyViewSet(ModelViewSet):
    queryset = Notify.objects.all()
    serializer_class = NotifySerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ('name')
    # filter_fields = ('name',)

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
            res = {'code': 500, 'msg': '该消息通知关联其他发布配置，请先删除关联的发布配置再操作！'}
            return Response(res)