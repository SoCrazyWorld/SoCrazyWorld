#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform 
@File ：Crontab.py
@IDE  ：PyCharm 
@Author ：JIM伟哥
@Date ：2022/4/25 13:29 
"""
"""存放定时任务业务函数"""
import requests
import json
from ToolPlatformApp.utils.TimeFunctions import now_time
from ToolPlatformApp.utils.EmailFunctions import send_mail, get_fm_email_list
from ToolPlatformApp.models import FmAlarmEmailConfig, CronJobsHistory, CronFunctionJobs
import logging
import time

logger = logging.getLogger("mylogger")
cron_logger = logging.getLogger("cron_logger")


def get_fm_alarm():
    base_url = FmAlarmEmailConfig.objects.all().filter(name="目标流量仪地址").first().value
    fm_alarm_url = "%s/wm/V1/fm/alarm/active_alerts" % base_url
    # fm_alarm_url = r"http://192.168.50.2:31604/wm/V1/fm/alarm/active_alerts"
    try:
        rp = requests.get(fm_alarm_url).text
        rp_json = json.loads(rp)
        alarm_list = rp_json['entries']
    except:
        logger.error("%s---获取流量仪报警列表失败" % now_time())
        alarm_list = []
    return alarm_list


def fm_alarm_num_check():
    alarm_list = get_fm_alarm()
    alarm_level = FmAlarmEmailConfig.objects.all().filter(name="报警边界").first().value
    alarm_nu = len(alarm_list)
    if alarm_nu < int(alarm_level):
        cron_logger.info("{0}--流量仪报警数量：{1}，当前边界为{2}，无需发送邮件".format("调度器任务触发", alarm_nu, alarm_level))
        return
    else:
        start_time = now_time().strftime('%Y-%m-%d %H:%M:%S')
        fun_job = CronFunctionJobs.objects.filter(fun_name='fm_alarm_num_check').first()
        mailto_list = get_fm_email_list()
        job_detail = "本次轮询监控发现报警{0}个，符合当前发送标准{1}，收件人：{2}".format(alarm_nu, alarm_level, mailto_list)
        CronJobsHistory.objects.create(job_id=fun_job.id, job_name=fun_job.fun_name, job_detail=job_detail,
                                       start_time=start_time)
        cron_logger.info(
            "内部业务函数【{0}】被触发，开始邮件通知，收件人：{3}，插入执行记录：{0}-{1}-{2}".format(fun_job.fun_name, fun_job.cron_exp, start_time,
                                                                      mailto_list))
        mail_title = '城投当前流量仪总报警数量:' + str(alarm_nu)
        tr0 = '当前流量仪总报警数量:' + str(alarm_nu)
        tr1 = '当前报警列表详情如下：'
        tr2 = '展示规则为：流量仪编号++报警类型++维保单位++最新更新时间++持续时间（小时）'
        mail_body_list = [tr0, tr1, tr2]
        for i in range(alarm_nu):
            if alarm_list[i]['latestTime'] is None:
                alarm_list[i]['latestTime'] = '无最新更新时间'
            if alarm_list[i]['alarmHour'] is None:
                alarm_list[i]['alarmHour'] = '无持续时间'
            trs = str(i + 1) + '#:  ' + alarm_list[i]['name'] + '++' + alarm_list[i][
                'alarmType'] + '++' + alarm_list[i]['maintainceUnit'] + '++' + \
                  alarm_list[i]['latestTime'] + '++' + str(alarm_list[i]['alarmHour'])
            mail_body_list.append(trs)
        mail_body = '\n'.join(mail_body_list)
        # print(mail_body)
        send_flag = send_mail(mailto_list, mail_title, mail_body)
        end_time = now_time().strftime('%Y-%m-%d %H:%M:%S')
        if send_flag:
            result = 'Y'
            err_mess = ""
        else:
            result = 'N'
            err_mess = "邮件发送失败，请排查"
        CronJobsHistory.objects.filter(job_id=fun_job.id).filter(job_name=fun_job.fun_name).filter(
            start_time=start_time).update(
            result=result, err_mess=err_mess, end_time=end_time)
        cron_logger.info("内部业务函数任务【{0}】执行结束，邮件成功发送,收件人：{1}，更新结束时间和结果到执行记录里".format(fun_job.fun_name, mailto_list))
        return
