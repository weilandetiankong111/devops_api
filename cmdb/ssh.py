import sys
import os
import paramiko
hostname = '192.168.5.155'
port = 22
username = 'yohanes'
password = '123456'
key_file = '/home/yohanes/.ssh'
# 将列表元素以空格拼接
cmd = " ".join(sys.argv[1:])
key_file = os.path.join(os.getcwd(), 'id_rsa')
def ssh_command(command):
   ssh = paramiko.SSHClient()
   # 指定key文件
   key = paramiko.RSAKey.from_private_key_file(key_file)
   # AutoAddPolicy()自动添加主机keys
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   # 连接主机信息
   ssh.connect(hostname, port, username, password, timeout=5)
   # 执行Shell命令，结果分别保存在标准输入，标准输出和标准错误
   stdin, stdout, stderr = ssh.exec_command('ls -l')
   stdout = stdout.read()
   error = stderr.read()
   # 判断stderr输出是否为空，为空则打印运行结果，不为空打印报错信息
   if not error:
      print(stdout)
   else:
      print(error)

   ssh.close()