from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth.models import User # django内置用户管理系统的Model
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password, check_password


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # serializer = self.serializer_class(data=request.data,context={'request':request})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            res = {'code': 200,'msg': '认证成功','token': token.key, 'username': user.username}
            return Response(res)
        else:
             res = {'code': 500,'msg': '用户们或密码错误'}
             return Response(res)

class ChangeUserPasswordView(APIView):
    def post(self,request):
        username = request.data.get('username')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(username=username)
        except:
            res = {'code': 500,'msg': '用户不存在'}
            return Response(res)

        # 判断原密码对不对
        if check_password(old_password, user.password):
            user.password = make_password(new_password) # 更新密码
            user.save()
            res = {'code': 200,'msg': '密码修改成功'}
        else:
            res = {'code': 500,'msg': '原密码不正确！'}
        return Response(res)