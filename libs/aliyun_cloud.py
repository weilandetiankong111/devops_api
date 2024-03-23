from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeRegionsRequest import DescribeRegionsRequest
from aliyunsdkecs.request.v20140526.DescribeZonesRequest import DescribeZonesRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeDisksRequest import DescribeDisksRequest
import json

class AliCloud():
    def __init__(self, secret_id, secret_key):
        self.secret_id = secret_id
        self.secret_key = secret_key

    # 地区
    def region_list(self):
        client = AcsClient(self.secret_id, self.secret_key)
        req = DescribeRegionsRequest()
        try:
            res = client.do_action_with_exception(req)
            data = json.loads(res.decode())
            return {'code': 200, 'data': data}
        except Exception as e:
            return {'code': 500, 'msg': e.get_error_msg()}

    # 可用区
    def zone_list(self, region_id):
        client = AcsClient(self.secret_id, self.secret_key)
        req = DescribeZonesRequest()
        req.add_query_param('RegionId', region_id)
        try:
            res = client.do_action_with_exception(req)
            data = json.loads(res.decode())
            return {'code': 200, 'data': data}
        except Exception as e:
            return {'code': 500, 'msg': e.get_error_msg()}
    # 实例
    def instance_list(self, region_id):
        client = AcsClient(self.secret_id, self.secret_key)
        req = DescribeInstancesRequest()
        req.add_query_param('RegionId', region_id)
        try:
            res = client.do_action_with_exception(req)
            data = json.loads(res.decode())
            return {'code': 200, 'data': data}
        except Exception as e:
            return {'code': 500, 'msg': e.get_error_msg()}
    # 实例关联的硬盘
    def instance_disk(self, instance_id):
        client = AcsClient(self.secret_id, self.secret_key)
        req = DescribeDisksRequest()
        req.add_query_param('InstanceId', instance_id)
        try:
            res = client.do_action_with_exception(req)
            data = json.loads(res.decode())
            return {'code': 200, 'data': data}
        except Exception as e:
            return {'code': 500, 'msg': e.get_error_msg()}

if __name__ == '__main__':
    cloud = AliCloud('LTAI5tB7BPcN6Jqm8ipgKSb9', 'G3tVeC797sQQqBntMRJhKgaaAsmK4H')
    # result = cloud.region_list()
    # result = cloud.zone_list('cn-beijing')
    result = cloud.instance_list('cn-beijing')
    # result = cloud.instance_disk('i-2zeffuf3e3uixm96jabc')
    print(result)


