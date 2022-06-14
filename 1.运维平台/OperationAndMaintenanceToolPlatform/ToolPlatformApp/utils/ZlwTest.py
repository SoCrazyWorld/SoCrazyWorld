#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform 
@File ：ZlwTest.py
@Comment : 
@IDE  ：PyCharm 
@Author ：JIM伟哥
@Date ：2022/6/2 12:29 
"""

import paramiko


def shell_script_execute(hostname, port, username, password, timeout, cmd, cron_exp, job_name, way):
    """执行shell命令的公共函数
    connect常用参数：
    hostname 连接的目标主机
    port=SSH_PORT 指定端口
    username=None 验证的用户名
    password=None 验证的用户密码
    timeout=None 可选的tcp连接超时时间
    allow_agent=True, 是否允许连接到ssh代理，默认为True 允许
    way:String 是定义调用途径的，来区分是手动单次触发还是定时器触发，希望入参：调度器定时触发和手动单次触发
    """
    # 一开始想判断当前job是不是执行状态,避免与后续手动单次触发冲突，但是触发器内的不好控制反馈情况，所以干脆默认进来调用的都是符合的，判断都放在外部单次调用的时候判断吧
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("-----进来了1----")
    client.connect(hostname=hostname, port=port, username=username, password=password, timeout=float(timeout))
    print("-----进来了2----")
    # 1、执行前，先把job的状态改为Y运行中
    stdin, stdout, stderr = client.exec_command(cmd)
    res = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    # finally:
    client.close()
    return res, err


if __name__ == '__main__':
    way = '触发器测试'
    res, err = shell_script_execute('192.168.20.3', '22', 'oracle', 'Orc@Inesa',
                                    '30', 'sh /home/oracle/test.sh', '*/1 * * * *', 'test',
                                    way)  # sh /home/oracle/test.sh
    print('res:' + res)
    print('Error:' + err)

# sftp_file_list('/upload/')
