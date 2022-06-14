#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：OperationAndMaintenanceToolPlatform 
@File ：Oracle.py
@Comment : 用于存放Oracle 直接撸SQL
@IDE  ：PyCharm 
@Author ：JIM伟哥
@Date ：2022/6/6 16:08 
"""

from django.db import connection, connections

"""以下操作记得先授权Django数据库配置用户的查询权限，否则无法查看系统表
grant select on v_$session to WM3POINT;
grant select on v_$process to WM3POINT;
grant select on v_$sqlarea to WM3POINT;
grant select on v_$locked_object to WM3POINT;
grant select on v_$parameter to WM3POINT;
grant select on sm$ts_avail to WM3POINT;
grant select on sm$ts_used to WM3POINT;
grant select on sm$ts_free to WM3POINT;
grant select on dba_free_space to WM3POINT;
grant select on dba_data_files to WM3POINT;
grant select on v_$sga to WM3POINT;
grant select on v_$sgastat to WM3POINT;
grant select on v_$pgastat to WM3POINT;
"""


def execute_sql(sql: str):
    # 获取游标对象
    cursor = connection.cursor()  # cursor = connections['default'].cursor()
    # 使用原生SQL进行查询
    cursor.execute(sql)
    # 获取所有的数据
    ret = cursor.fetchall()
    cursor.close()
    # print(type(ret)) # 返回的是个list，里面是元组
    return ret


def orc_session_count():
    """获取oracle当前session数量"""
    sql = "select count(*) from v$session"
    res = execute_sql(sql)
    count = res[0][0]
    return count


def orc_process_count():
    """获取oracle当前process数量"""
    sql = "select count(*) from v$process"
    res = execute_sql(sql)
    count = res[0][0]
    return count


def orc_no_sys_session_count():
    """获取oracle当前排除系统用户SYS之外的session数量"""
    sql = "select count(*) from v$session where SCHEMANAME <>'SYS'"
    res = execute_sql(sql)
    count = res[0][0]
    return count


def orc_active_session_count():
    """获取oracle当前并发连接数"""
    sql = "select count(*) from v$session where status='ACTIVE'"
    res = execute_sql(sql)
    count = res[0][0]
    # print(count)
    return count


def orc_max_session_set():
    """获取oracle当前最大会话连接数设置"""
    sql = "select value from v$parameter where name = 'sessions'"
    res = execute_sql(sql)
    count = res[0][0]
    # print(count)
    return count


def orc_max_process_set():
    """获取oracle当前最大进程连接数设置"""
    sql = "select value from v$parameter where name = 'processes'"
    res = execute_sql(sql)
    count = res[0][0]
    # print(count)
    return count


def orc_session_list():
    """获取oracle当前非SYS连接数列表详情"""
    sql = """select  a.USERNAME, a.STATUS, a.SCHEMANAME, a.OSUSER, a.MACHINE, a.LOGON_TIME, a.LAST_CALL_ET, a.STATE, c.sql_text 正在执行的SQL,c.SQL_FULLTEXT
from v$session a
left join V$process b on a.paddr=b.addr
left join v$sqlarea c on a.sql_hash_value = c.hash_value
where a.SCHEMANAME <>'SYS' ORDER BY a.MACHINE"""
    res_list = execute_sql(sql)
    return res_list


def orc_service_sess_list():
    """获取各服务session占用情况"""
    sql = """select a.SCHEMANAME, a.MACHINE, a.OSUSER, a.STATUS, count(*)
            from v$session a
            left join V$process b on a.paddr=b.addr
            left join v$sqlarea c on a.sql_hash_value = c.hash_value
            where a.SCHEMANAME <>'SYS'
            group by a.MACHINE,a.SCHEMANAME, a.OSUSER,a.STATUS
            ORDER BY count(*) DESC"""
    res_list = execute_sql(sql)
    # print(res_list)
    return res_list


def orc_deadlock_list():
    """获取oracle当前死锁数"""
    sql = "select username,lockwait,status,machine,program from v$session where sid in (select session_id from v$locked_object)"
    res_list = execute_sql(sql)
    # print(res_list)
    return res_list


def orc_tablespace_total():
    """获取oracle当前表空间总使用率，但是要注意这里的总量不是不会变，因为数据文件是自动自增的，会不断变大的"""
    sql = """SELECT a.tablespace_name "Tablespace",
            trunc(a.bytes/1024/1024,0) "Total(M)",
            trunc(b.bytes/1024/1024,0) "Used(M)",
            trunc((a.bytes-b.bytes)/1024/1024,0) "Free(M)",
            substr((b.bytes * 100) / a.bytes,0,4) "% USED "
            FROM sys.sm$ts_avail a, sys.sm$ts_used b
            WHERE a.tablespace_name = b.tablespace_name
            """
    res_list = execute_sql(sql)
    # print(res_list)
    return res_list


def orc_tablespace_file():
    """获取oracle当前表空间数据文件使用情况"""
    sql = """select
        　　b.tablespace_name 表空间,
        　　b.file_name 物理文件名,
        　　trunc(b.bytes/1024/1024,0) 大小M,
        　　trunc((b.bytes-sum(nvl(a.bytes,0)))/1024/1024,0) 已使用M,
        　　trunc((b.bytes-sum(nvl(a.bytes,0)))/(b.bytes)*100,2) 利用率
        　　from dba_free_space a,dba_data_files b
        　　where a.file_id=b.file_id
        　　group by b.tablespace_name,b.file_name,b.bytes
        　　order by b.tablespace_name,b.file_name
        """
    res_list = execute_sql(sql)
    # print(res_list)
    return res_list


def orc_sga_pga():
    """获取oracle当前SGA和PGA使用情况"""
    sql = """select name,total,round(total-free,0) used, round(free,0) free,round((total-free)/total*100,2) pctused from
            (select 'SGA' name,(select sum(value/1024/1024) from v$sga) total,
            (select sum(bytes/1024/1024) from v$sgastat where name='free memory')free from dual)
            union
            select name,total,round(used,0)used,round(total-used,0)free,round(used/total*100,2)pctused from (
            select 'PGA' name,(select value/1024/1024 total from v$pgastat where name='aggregate PGA target parameter')total,
            (select value/1024/1024 used from v$pgastat where name='total PGA allocated')used from dual)
        """
    res_list = execute_sql(sql)
    # print(res_list)
    return res_list
