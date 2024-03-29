from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from system_config.serializers import CredentialSerializer
from system_config.models import Credential

class CredentialViewSet(ModelViewSet):
    queryset = Credential.objects.all()  # 指定操作的数据
    serializer_class = CredentialSerializer  # 指定序列化器

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]  # 指定过滤器
    search_fields = ('name',)  # 指定可搜索字段
    filter_fields = ('name',)  # 指定过滤字段

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
            res = {'code': 500, 'msg': '该凭据机房关联其他主机，请先删除关联的主机再操作！！'}
            return Response(res)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        res = {'code': 200,'msg': '创建成功！'}
        return Response(res)