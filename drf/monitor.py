import datetime
import socket
import sys

from supervisor import childutils


def main():
    while True:
        headers, payload = childutils.listener.wait(sys.stdin, sys.stdout)
        # 通过判断headers的状态来判断supervisor是否正常
        print('+++++++++++++++++++++++++')
        print(headers)
        # 获取主机名
        hostname = socket.gethostname()
        # 获取IP
        ip = socket.gethostbyname(hostname)
        now = datetime.datetime.now().strftime('%Y-%m-%d %X')
        msg = '{} 服务被重启,非正常发版请仔细核实服务状态 {}'.format(now, ip)
        print(msg)
        print('-------------------------')
        childutils.listener.ok(sys.stdout)