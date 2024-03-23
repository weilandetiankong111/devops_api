from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models

class TCloud():
    def __init__(self, secret_id, secret_key):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.cred = credential.Credential(self.secret_id, self.secret_key)

    def region_list(self):
        client = cvm_client.CvmClient(self.cred, None)
        req = models.DescribeRegionsRequest()  # 获取地区
        try:
            resp = client.DescribeRegions(req)  # resp=[{"Region": "ap-guangzhou", "RegionName": "华南地区(广州)", "RegionState": "AVAILABLE"}, ]
            resp.code = 200
            return resp
        except TencentCloudSDKException as e:
            return {'code': '500', 'msg': e.message}

    def zone_list(self, region_id):
        client = cvm_client.CvmClient(self.cred, region_id)
        req = models.DescribeZonesRequest()
        try:
            resp = client.DescribeZones(req)
            resp.code = 200
            return resp
        except TencentCloudSDKException as e:
            return {'code': '500', 'msg': e.message}

    def instance_list(self, region_id):
        client = cvm_client.CvmClient(self.cred, region_id)  # 获取北京区域
        req = models.DescribeInstancesRequest()
        try:
            resp = client.DescribeInstances(req)
            resp.code = 200
            return resp
        except TencentCloudSDKException as e:
            return {'code': '500', 'msg': e.message}

if __name__ == '__main__':
    cloud = TCloud("AKIDJaox2BMemv5A92hKm5EE8tUuHTfmnU6a", "XzJVZVIzYzHVboxyukV9f2IVbZROLBsT")
    result = cloud.region_list()
    # result = cloud.zone_list('ap-shanghai')
    # result = cloud.instance_list("ap-shanghai")
    print(result)
