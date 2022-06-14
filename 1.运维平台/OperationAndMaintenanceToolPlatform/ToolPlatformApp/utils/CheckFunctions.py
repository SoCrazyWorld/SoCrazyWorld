#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform
@File ：EmailFunctions.py
@IDE  ：PyCharm
@Author ：JIM伟哥
@Date ：2022/4/24 18:26
"""
import re

"""本包用于存放各种校验函数等工具函数"""


def email_isvalid(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@(163|qq|foxmail|icity.inesa)\.com')
    if re.fullmatch(regex, email):
        return True
    else:
        return False
