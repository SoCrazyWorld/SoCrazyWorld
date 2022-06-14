#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform 
@File ：Crontab.py
@Comment : 此类用于存放APScheduler定时的相关基础方法
@IDE  ：PyCharm 
@Author ：JIM伟哥
@Date ：2022/5/24 16:34 
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from ToolPlatformApp.models import CronJobs, CronFunctionJobs
from ToolPlatformApp.utils.ShellCMD import shell_script_execute
from ToolPlatformApp.BusinessFunction import fm_alarm_num_check
import logging

logger = logging.getLogger("mylogger")
cron_logger = logging.getLogger("cron_logger")


def scheduler_init():
    """初始化一个调度器"""
    # way = '直接引用函数测试'
    # job = CronJobs.objects.filter(name='20.2WM3GIS备份').first()
    # shell_script_execute(job.remote_ip, job.remote_port, job.remote_name, job.remote_password,
    #                                                  job.timeout, job.remote_cmd, job.cron_exp, job.name, way)
    scheduler = get_scheduler()
    # 初始化调度器
    scheduler = sched_jobs_reload(scheduler)
    # from apscheduler.triggers.cron import CronTrigger
    # scheduler.add_job(func=test, id='test', trigger=CronTrigger.from_crontab('*/1 * * * *'))
    sched_start(scheduler)
    cron_logger.info("启动初始化后调度器任务：" + str(scheduler.get_jobs()))
    return scheduler


def get_scheduler():
    """定义调度器，线程数先写死了，后续再拓展提出来优化"""
    executors = {
        'default': ThreadPoolExecutor(max_workers=30),
    }
    job_defaults = {
        'coalesce': True,  # 如果系统因为某些原因没有执行任务，导致任务累计，为True只运行最后一次，为False则累计的任务全部跑一遍。
        'max_instances': 1  # 默认情况下，每个作业只能同时运行一个实例。该参数可以为调度程序设置允许并发运行的特定作业的最大实例。
    }
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai', executors=executors, job_defaults=job_defaults)

    return scheduler


def sched_job_add(scheduler, func, args, exp, job_name):
    """新增定时job
    func参数：根据官方文档需传可调用对象，而不是一个字符串，不然会报非法参数Invalid reference
    """
    scheduler.add_job(id=job_name, func=func, args=args, trigger=CronTrigger.from_crontab(exp))


def sched_job_delete(scheduler, job_name):
    """# 删除定时job"""
    scheduler.pause_job(job_name)
    scheduler.remove_job(job_name)


def sched_jobs_get(scheduler):
    """# 查询当前所有定时job"""
    return scheduler.get_jobs()


def sched_job_exist_or_not(scheduler, job_id):
    """判断指定job是否存在于当前调度器中，用于判断是否需要加入"""
    jobs_exist = sched_jobs_get(scheduler)
    for job in jobs_exist:
        if job.id == job_id:
            return True
    return False


def sched_start(scheduler):
    """启动调度器"""
    scheduler.start()


def sched_shutdown(scheduler):
    """关闭调度器"""
    scheduler.shutdown()


def sched_jobs_reload_flag():
    """判断当前job是否可以重新装载，避免有执行中的job"""
    job_run_list = CronJobs.objects.all().filter(current_status="Y")
    cron_logger.info("发现处于运行中状态的任务：" + str(len(job_run_list)) + "个")
    if len(job_run_list) != 0:
        return False
    else:
        cron_logger.info("当前无运行中的任务，具备执行重载调度器条件，调度器初始化中....")
        return True


def sched_jobs_reload(scheduler):
    """重新装载所有定时任务给调度器"""
    # 定义调用触发途径，来区分手动触发，方便日志记录
    way = "调度器定时触发"
    if sched_jobs_reload_flag():
        scheduler.remove_all_jobs()
        # 添加启用状态的jobs
        jobs_list = CronJobs.objects.all().filter(use_flag='Y')
        cron_logger.info("即将重新装载{0}个已启用job到调度器".format(len(jobs_list)))
        for job in jobs_list:
            sched_job_add(scheduler,
                          shell_script_execute, (job.remote_ip, job.remote_port, job.remote_name, job.remote_password,
                                                 job.timeout, job.remote_cmd, job.cron_exp, job.name, way),
                          job.cron_exp, job.name)
        cron_logger.info("已完成重新装载{0}个已启用job到调度器".format(len(jobs_list)))
        # 装载内部业务函数
        fun_job_list = CronFunctionJobs.objects.filter(use_flag='Y')
        cron_logger.info("装载内部业务函数定时任务：{0}个".format(len(fun_job_list)))
        for fun_job in fun_job_list:
            sched_job_add(scheduler, eval(fun_job.fun_name), eval(fun_job.fun_args), fun_job.cron_exp,
                          fun_job.fun_name)
            cron_logger.info(
                "成功装载内部业务函数定时任务：【{0}】,传参：【{1}】，Cron:【{2}】".format(fun_job.fun_name, fun_job.fun_args, fun_job.cron_exp))
        # cron_logger.info("单独装载内部函数定时任务：流量仪报警监控邮件【FM_Alarm】")
        # sched_job_add(scheduler=scheduler, func=fm_alarm_num_check, args=(), exp='*/30 * * * *', job_name='FM_Alarm')
        cron_logger.info("最新调度器任务清单：" + str(sched_jobs_get(scheduler)))
    else:
        cron_logger.info("当前有运行中的任务，不具备执行重载调度器条件。请检查数据库任务状态。")
    return scheduler
