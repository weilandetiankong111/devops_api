from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
# 序列化
from cmdb.models import Idc,ServerGroup,Server
from cmdb.serializers import IdcSerializer,ServerGroupSerializer,ServerSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

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