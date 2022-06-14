#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform
@File ：EmailFunctions.py
@IDE  ：PyCharm
@Author ：JIM伟哥
@Date ：2022/4/25 11:26
"""
import smtplib
from email.mime.text import MIMEText
from ToolPlatformApp.models import FmAlarmEmail
import logging

logger = logging.getLogger("mylogger")

# mailto_list = ['***']  # 收件人(列表)
mail_host = "smtp.ym.163.com"
mail_user = "***"
mail_pass = "****"


def get_fm_email_list():
    email_list = []
    email_list_ob = FmAlarmEmail.objects.all().filter(use_flag='Y')
    for ob in email_list_ob:
        email_list.append(ob.email)
    if len(email_list) == 0:
        email_list = ['***', '**']
    return email_list


def send_mail(to_list, sub, content):
    me = "运维ZLW" + "<" + mail_user + ">"
    msg = MIMEText(content, _subtype='plain')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        logger.info("邮件发送成功")
        return True
    except smtplib.SMTPException:
        logger.error("Error: 无法发送邮件")
        return False

# if __name__ == '__main__':
# send_mail(mailto_list,"城投当前流量仪总报警数量","测试")
