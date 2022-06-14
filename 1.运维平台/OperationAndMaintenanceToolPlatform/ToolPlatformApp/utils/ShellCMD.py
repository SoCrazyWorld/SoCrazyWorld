#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform 
@File ：ShellCMD.py
@Comment : 本类用于存放Linux相关shell执行操作函数
@IDE  ：PyCharm 
@Author ：JIM伟哥
@Date ：2022/5/24 18:57 
"""
import paramiko
import logging
from ToolPlatformApp.models import CronJobs, CronJobsHistory
from ToolPlatformApp.utils.TimeFunctions import now_time

"""本次选择了paramiko模块，因为此模块支持免密也支持密码登录，然后还同时有SSHClient和SFTPClient两大部分，完美支撑需要；
还研究了commands模块以及subprocess模块，甚至原生的os，不是要提前配置免密就是不支持结果等收集，对于平台支撑未知服务器不友好，所以弃用了。
"""
cron_logger = logging.getLogger("cron_logger")
logger = logging.getLogger("mylogger")


def sftp_file_list(hostname, port, username, password, timeout, dir):
    """查看指定路径的sftp文件列表"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    client.connect(hostname=hostname, port=port, username=username, password=password, timeout=timeout)
    sftp = paramiko.SFTPClient.from_transport(client.get_transport())
    list = sftp.listdir(dir)
    print(list)


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
    res = None
    err = None
    result = None
    err_mess = None
    job_sp = CronJobs.objects.filter(name=job_name).first()
    job_id = job_sp.id
    job_detail = "【{3}】{0}@{1}:{2}".format(job_sp.remote_ip, job_sp.remote_port, job_sp.remote_cmd, way)
    # cron_logger.info("-----进来了1----")
    start_time = now_time().strftime('%Y-%m-%d %H:%M:%S')
    try:
        CronJobsHistory.objects.create(job_id=job_id, job_name=job_name, job_detail=job_detail, start_time=start_time)
        cron_logger.info("任务【{0}】被触发，插入执行记录：{1}-{0}-{2}-{3}".format(job_name, job_id, job_detail, start_time))
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # cron_logger.info("-----进来了2----")
        client.connect(hostname=hostname, port=port, username=username, password=password, timeout=float(timeout))
        # cron_logger.info("-----进来了3----")
        # 1、执行前，先把job的状态改为Y运行中
        CronJobs.objects.filter(name=job_name).update(current_status='Y')
        # cron_logger.info("-----进来了4----")
        # 执行多个命令，可使用分号隔开：exec_command('cd /home;ls -l')
        cron_logger.info(
            "{6}-开始执行【{0}】： {1}@{2}:{3}  {4},crontab表达式：{5}".format(job_name, username, hostname, port, cmd, cron_exp,
                                                                    way))
        stdin, stdout, stderr = client.exec_command(cmd)

        res = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        cron_logger.info('执行结果:' + res)
        cron_logger.info('报错信息:' + err)
        cron_logger.info(
            "{6}-结束执行【{0}】： {1}@{2}:{3}  {4},crontab表达式：{5}".format(job_name, username, hostname, port, cmd, cron_exp,
                                                                    way))
        # 执行后，先把job的状态改为N就绪
        CronJobs.objects.filter(name=job_name).update(current_status='N')

        # 执行记录插入历史表
        result = 'Y'  # "命令已运行，返回结果失败："
        err_mess = ('res:' + res + ';err:' + err)[:1900]
    except Exception as e:
        cron_logger.error(e)
        result = 'N'
        err_mess = "SSH连接异常，命令未运行"
        cron_logger.error("SSH连接异常，本次执行失败")
    finally:
        client.close()
        end_time = now_time().strftime('%Y-%m-%d %H:%M:%S')
        CronJobsHistory.objects.filter(job_id=job_id).filter(job_name=job_name).filter(start_time=start_time).update(
            result=result, err_mess=err_mess,
            end_time=end_time)
        cron_logger.info("任务【{0}】执行结束，更新结束时间和结果到执行记录里".format(job_name))
        return res, err

# if __name__ == '__main__':
# res, err = shell_script_execute('sh /home/oracle/test.sh')  # sh /home/oracle/test.sh
# print('res:' + res)
# print('Error:' + err)

# sftp_file_list('/upload/')
