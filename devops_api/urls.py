from django.contrib import admin
from django.urls import path, include, re_path

from libs.token_auth import CustomAuthToken,ChangeUserPasswordView
from cmdb.views import HostCollectView, CreateHostView, ExcelCreateHostView, AliyunCloudView, TencentCloudView
from app_release.views import GitView, DeployView, RollbackView,ApplyEchartView

from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='接口文档')

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^api/docs/$', schema_view),
    re_path('^api/login/$', CustomAuthToken.as_view()),
    re_path('^api/change_password/$', ChangeUserPasswordView.as_view()),
    re_path('^api/cmdb/host_collect/$', HostCollectView.as_view()),
    re_path('^api/cmdb/create_host/$', CreateHostView.as_view()),
    re_path('^api/cmdb/excel_create_host/$', ExcelCreateHostView.as_view()),
    re_path('^api/cmdb/aliyun_cloud/$', AliyunCloudView.as_view()),
    re_path('^api/cmdb/tencent_cloud/$', TencentCloudView.as_view()),
    re_path('^api/app_release/git/$', GitView.as_view()),
    re_path('^api/app_release/deploy/$', DeployView.as_view()),
    re_path('^api/app_release/rollback/$', RollbackView.as_view()),
    re_path('^api/app_release/apply_echart/$', ApplyEchartView.as_view()),
]

# CMDB系统
from cmdb.views import IdcViewSet, ServerViewSet, ServerGroupViewSet
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'cmdb/idc', IdcViewSet, basename='idc')
router.register(r'cmdb/server_group', ServerGroupViewSet, basename='server_group')
router.register(r'cmdb/server', ServerViewSet, basename='server')

# 发布系统
from app_release.views import EnvViewSet, ProjectViewSet, AppViewSet, ReleaseConfigViewSet, ReleaseApplyViewSet
router.register(r'app_release/env', EnvViewSet, basename='env')
router.register(r'app_release/project', ProjectViewSet, basename='project')
router.register(r'app_release/app', AppViewSet, basename='app')
router.register(r'app_release/config', ReleaseConfigViewSet, basename='config')
router.register(r'app_release/apply', ReleaseApplyViewSet, basename='apply')

# 系统配置
from system_config.views import CredentialViewSet, NotifyViewSet
router.register(r'config/credential', CredentialViewSet, basename='credential')
router.register(r'config/notify', NotifyViewSet, basename='notify')

urlpatterns += [
    path('api/', include(router.urls))
]
