import requests
import json

def dingtalk_msg(url, content):
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
    res = requests.post(url=url, headers=headers, data=json.dumps(data))
    return res.text
if __name__ == "__main__":
    content = "发布成功啦！！！"
    url = "https://oapi.dingtalk.com/robot/send?access_token=2a6fa38cc9230812f418f861269581ebfbe4d2df82bce76101383b6e8d2859b6"
    print(dingtalk_msg(url, content))