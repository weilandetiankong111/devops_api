import paramiko
from io import StringIO
import os

class SSH():
    def __init__(self, ip, port, username, password=None, key=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.key = key

    def command(self, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.password:
                ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password, timeout=5)
            else:
                cache = StringIO(self.key)  # 将文本转为文件对象
                key = paramiko.RSAKey.from_private_key(cache)
                ssh.connect(hostname=self.ip, port=self.port, username=self.username, pkey=key)

            stdin, stdout, stderr = ssh.exec_command(command)
            stdout = stdout.read()
            error = stderr.read()
            if not error:
                ssh.close()
                return {'code': 200, 'msg': '执行命令成功！', 'data': stdout}
            else:
                ssh.close()
                return {'code': 500, 'msg': '执行命令失败！错误：%s' %error}
        except Exception as e:
            return {'code': 500, 'msg': 'SSH连接失败！错误：%s' %e}

    def scp(self, local_file, remote_file):
        try:
            s = paramiko.Transport((self.ip, self.port))
            if self.password:
                s.connect(username=self.username, password=self.password)
            else:
                cache = StringIO(self.key)  # 将文本转为文件对象
                key = paramiko.RSAKey.from_private_key(cache)
                s.connect(username=self.username, pkey=key)

            sftp = paramiko.SFTPClient.from_transport(s)
            try:
                sftp.put(local_file, remote_file)
                s.close()
                return "上传文件成功"
            except Exception  as e:
                return "上传文件失败：%s" %s
        except Exception as e:
            return "SSH连接失败：%s" %e

    def test(self):
        result = self.command('ls')
        return result

if __name__ == '__main__':
    ssh = SSH('47.101.143.116', 22, 'root', 'aolazhuwangA1')
    local_file = os.path.join(os.getcwd(), 'id_rsa')
    result = ssh.command('ls -l')
    # result = ssh.scp(local_file, '/tmp/agent.py')
    print(result)