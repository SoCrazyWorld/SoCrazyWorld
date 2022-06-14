#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform
@File ：EmailFunctions.py
@IDE  ：PyCharm
@Author ：JIM伟哥
@Date ：2022/4/25 11:16
"""
import time
from datetime import datetime

"""本函数包用于存放各种公共时间处理函数，如延时等"""


def delay_seconds(num: int):
    """妙级别延时函数"""
    time.sleep(num)


def delay_minutes(num: int):
    """分钟级别延时函数"""
    time.sleep(num * 60)


def delay_hours(num: int):
    """小时级别延时函数"""
    time.sleep(num * 60 * 60)


def now_time():
    return datetime.now()
