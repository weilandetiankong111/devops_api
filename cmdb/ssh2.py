import os,paramiko
hostname = '192.168.5.155'
port = 22
username = 'yohanes'
password = '123456'
local_path = os.path.join(os.getcwd(), 'id_rsa')
remote_path =  '/home/yohanes/id_rsa'
# 指定实例
s = paramiko.Transport(hostname,port)
s.connect(username=username,password=password)
sftp = paramiko.SFTPClient.from_transport(s)
sftp.put(local_path, remote_path)
