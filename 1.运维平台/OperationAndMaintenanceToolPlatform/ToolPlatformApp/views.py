from django.shortcuts import render, redirect
from django.http import HttpResponse
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from ToolPlatformApp.models import FmAlarmEmail
from ToolPlatformApp.utils.CheckFunctions import email_isvalid
from ToolPlatformApp.BusinessFunction import get_fm_alarm
from ToolPlatformApp.models import FmAlarmEmailConfig, CronJobs, CronJobsHistory, CronFunctionJobs
import logging
from ToolPlatformApp.utils.Crontab import scheduler_init, sched_jobs_reload, sched_jobs_get, \
    sched_job_exist_or_not, sched_job_add, sched_job_delete
from ToolPlatformApp.utils import Oracle

logger = logging.getLogger("mylogger")
cron_logger = logging.getLogger("cron_logger")

# 初始化一个调度器
scheduler = scheduler_init()


def test():
    # from ToolPlatformApp.utils.Oracle import orc_active_session_count,orc_deadlock_count
    #
    # orc_active_session_count()
    # orc_deadlock_count()
    pass


def home(request):
    """平台主页"""
    return render(request, "home.html", {'navbarflag': "home"})


def fm_email(request):
    """流量仪当前报警查看以及邮件通知列表维护"""
    # 报警数据处理
    alarm_num = len(get_fm_alarm())
    # 邮箱数据处理
    email_list = FmAlarmEmail.objects.all().order_by('id')
    use_email_list = FmAlarmEmail.objects.all().filter(use_flag="Y")
    use_num = len(use_email_list)
    message = ""
    # 脚本配置处理
    if request.method == "GET":
        fm_address = FmAlarmEmailConfig.objects.all().filter(name="目标流量仪地址").first().value
        fm_alarm_level = FmAlarmEmailConfig.objects.all().filter(name="报警边界").first().value
    else:
        fm_address = request.POST.get("fm_address")
        fm_alarm_level = request.POST.get("fm_alarm_level")
        if fm_address == "" or fm_alarm_level == "":
            fm_address = FmAlarmEmailConfig.objects.all().filter(name="目标流量仪地址").first().value
            fm_alarm_level = FmAlarmEmailConfig.objects.all().filter(name="报警边界").first().value
            message = "不允许为空"
        else:
            FmAlarmEmailConfig.objects.all().filter(name="目标流量仪地址").update(value=fm_address)
            FmAlarmEmailConfig.objects.all().filter(name="报警边界").update(value=fm_alarm_level)
            message = "配置已更新"
    return render(request, "fm_email.html", {'email_list': email_list, 'use_num': use_num, 'alarm_num': alarm_num,
                                             'fm_address': fm_address, 'fm_alarm_level': fm_alarm_level,
                                             'message': message, 'navbarflag': "fmalarm"})


def fm_email_add(request):
    """新增流量仪报警邮件通知收件人"""
    context = {
        'flag_choice': FmAlarmEmail.flag_choice,
        'navbarflag': "fmalarm"
    }
    if request.method == "GET":
        return render(request, 'fm_email_add.html', context)
    name = request.POST.get('name')
    email = request.POST.get('email')
    use_flag = request.POST.get('flag')
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # print(create_time)
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 邮箱格式检验
    if email_isvalid(email):
        # 判断输入邮箱是否已存在
        obs = FmAlarmEmail.objects.all()
        flag = 0
        for o in obs:
            if email == o.email:
                flag = 1
                break
        if flag == 1:
            error_message = "输入邮箱已存在，请重新输入"
            return render(request, "fm_email_add.html",
                          {'flag_choice': context['flag_choice'], 'name': name, 'email': email,
                           'use_flag': use_flag,
                           'error_message': error_message, 'navbarflag': "fmalarm"})
        else:
            # 添加到数据库中
            FmAlarmEmail.objects.create(name=name, email=email, use_flag=use_flag,
                                        create_time=create_time, update_time=update_time
                                        )
            return redirect("/fm/email")
    else:
        error_message = "邮箱输入格式有误，请重新输入"
        return render(request, "error.html", {"error_message": error_message, 'navbarflag': "fmalarm"})


def fm_email_delete(request, nid):
    """删除流量仪报警邮件通知收件人"""
    id_db = FmAlarmEmail.objects.all().filter(id=nid)
    if (nid is None) or (len(id_db) < 1):
        message = "删除邮箱对应ID不存在或者为空，请刷新后尝试"
        # return render(request, "error.html", {"error_message": message})
    else:
        name = FmAlarmEmail.objects.all().filter(id=nid)[0].name
        email = FmAlarmEmail.objects.all().filter(id=nid)[0].email
        FmAlarmEmail.objects.all().filter(id=nid).delete()
        log_str = "{0}--删除收件人{1}的邮箱：{2}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name, email)
        logger.info(log_str)
        # return redirect("/fm/email")
        message = "{0}的邮箱{1}已删除成功".format(name, email)
    return HttpResponse(message)


def fm_email_update(request, nid):
    """修改流量仪报警邮件通知收件人"""
    ob = FmAlarmEmail.objects.all().filter(id=nid).first()
    flag_choice = FmAlarmEmail.flag_choice
    error_message = ''
    if request.method == "GET":
        return render(request, "fm_email_update.html",
                      {"ob": ob, 'flag_choice': flag_choice, 'error_message': error_message,
                       'navbarflag': "fmalarm"})
    name = request.POST.get('name')
    email = request.POST.get('email')
    use_flag = request.POST.get('flag')
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 先邮箱格式检验
    if email_isvalid(email):
        if use_flag == ob.use_flag and name == ob.name and email == ob.email:
            error_message = "未发生任何改动，请重新输入"
            return render(request, "fm_email_update.html",
                          {"ob": ob, 'flag_choice': flag_choice, 'error_message': error_message,
                           'navbarflag': "fmalarm"})
        elif email == ob.email and (use_flag != ob.use_flag or name != ob.name):
            # 添加到数据库中
            FmAlarmEmail.objects.filter(id=nid).update(name=name, email=email, use_flag=use_flag,
                                                       update_time=update_time)
            logger.info("{0}邮箱被修改，最新配置：{1}，启用状态{2}".format(name, email, use_flag))
            return redirect("/fm/email")
        else:
            # 判断输入邮箱是否已存在
            obs = FmAlarmEmail.objects.all().exclude(id=nid)
            flag = 0
            for o in obs:
                if email == o.email:
                    flag = 1
                    break
            if flag == 1:
                ob.email = email
                error_message = "输入邮箱已存在，请重新输入"
                return render(request, "fm_email_update.html",
                              {"ob": ob, 'flag_choice': flag_choice, 'error_message': error_message,
                               'navbarflag': "fmalarm"})
            else:
                FmAlarmEmail.objects.filter(id=nid).update(name=name, email=email, use_flag=use_flag,
                                                           update_time=update_time)
                logger.info("{0}的邮箱被修改，最新配置：{1}，启用状态{2}".format(name, email, use_flag))
                return redirect("/fm/email")
    else:
        ob.email = email
        error_message = "邮箱格式有误，请重新输入"
        return render(request, "fm_email_update.html",
                      {"ob": ob, 'flag_choice': flag_choice, 'error_message': error_message,
                       'navbarflag': "fmalarm"})
        # return render(request, "error.html", {"error_message": error_message})

    # Create your views here.


def eureka_get(request):
    """获取当前指定地址的所有注册服务"""
    if (request.GET.get("address") is None):
        URL = "http://192.168.50.2:32123/"
    else:
        URL = request.GET.get("address")
    eureka_list = []
    message = ""
    try:
        rp = requests.get(URL)
        bs = BeautifulSoup(rp.text, 'html.parser')
        tb_rp = bs.find_all('table')[2].find('tbody')
        for tr in tb_rp.find_all('tr'):
            app = tr.find_all('td')[0]
            pod = tr.find_all('td')[3]
            for a in pod.find_all('a'):
                # print(a.text)
                b_t = (app.text, a.text)
                eureka_list.append(b_t)
            # print(eureka_list)
    except:
        message = "输入地址无法访问,请检查"
    return render(request, "eureka.html",
                  {"eureka_list": eureka_list, "count": len(eureka_list), "eureka_url": URL, "message": message,
                   'navbarflag': "eureka"})


def eureka_delete(request):
    """从eureka上删除指定注册服务"""
    baseurl = request.GET.get("url")
    # print(url)
    if baseurl[-1] != '/':
        baseurl = baseurl + '/'
    app = request.GET.get("app")
    pod = request.GET.get("pod")
    url = "{0}eureka/apps/{1}/{2}".format(baseurl, app, pod)
    nt = datetime.now()
    try:
        requests.delete(url)
        # raise Exception('主动异常')
        logger.log("{0}--成功删除服务：{1}".format(nt, url))
        message2 = "%s删除成功" % pod
    except:
        logger.error("{0}--删除服务失败：{1}".format(nt, url))
        message2 = "%s删除失败" % pod
    # return redirect("/eureka/get?address={0}&message2={1}".format(baseurl, message2))
    return HttpResponse(message2)


def cron_job(request):
    """定时任务查看"""
    all_jobs = CronJobs.objects.all()
    # 获得目前已加入调度器的任务数量
    sche_jobs = sched_jobs_get(scheduler)
    job_add_num = len(sche_jobs)
    # 获取目前正在运行中的脚本任务数量
    running_jobs = CronJobs.objects.filter(current_status='Y')
    job_running_num = len(running_jobs)
    # 获取内部业务函数定时任务列表（因为牵涉内部业务代码函数，此列表不支持页面新增，仅支持定时等修改）
    fun_job_all = CronFunctionJobs.objects.all()
    return render(request, "cron_job.html",
                  {'job_add_num': job_add_num, 'job_running_num': job_running_num, 'jobs': all_jobs,
                   'fun_jobs': fun_job_all, 'navbarflag': "cron", "message": ""})


def cron_job_add(request):
    """已加入调度器中的定时任务"""
    context = {
        'flag_choice': CronJobs.flag_choice,
        'navbarflag': "cron"
    }
    if request.method == "GET":
        return render(request, 'cron_job_add.html', context)
    name = request.POST.get('name')
    remote_ip = request.POST.get('remote_ip')
    remote_port = request.POST.get('remote_port')
    remote_cmd = request.POST.get('remote_cmd')
    remote_name = request.POST.get('remote_name')
    remote_password = request.POST.get('remote_password')
    timeout = request.POST.get('timeout')
    cron_exp = request.POST.get('cron_exp')
    use_flag = request.POST.get('use_flag')
    comment = request.POST.get('comment')
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    CronJobs.objects.create(name=name, remote_ip=remote_ip, remote_port=remote_port, remote_cmd=remote_cmd,
                            remote_name=remote_name, remote_password=remote_password, timeout=timeout,
                            cron_exp=cron_exp, use_flag=use_flag, comment=comment, update_time=update_time)
    way = "调度器定时触发"
    cron_logger.info("新增前--调度器最新任务列表：" + str(sched_jobs_get(scheduler)))
    if use_flag == 'Y':
        # 判断目前调度器里是否存在,如果存在先删掉，再添加新的
        # if sched_job_exist_or_not(scheduler, name):
        #     sched_job_delete(scheduler, name)
        #     cron_logger.info("任务新增,调度器已删除旧配置的定时任务【{0}】".format(name))
        # sched_job_add(scheduler,
        #               shell_script_execute, (remote_ip, remote_port, remote_name, remote_password,
        #                                      timeout, remote_cmd, cron_exp, name, way),
        #               cron_exp, name)
        # 为避免调度器莫名其妙任务不跑，暂定每次新增修改都自动初始化一下调度器
        sched_jobs_reload(scheduler)
        cron_logger.info("任务新增，新增定时任务【{0}】到调度器中,命令为：{1}，定时为：{2}。".format(name, remote_cmd, cron_exp))
    else:
        # 判断目前调度器里是否存在
        if sched_job_exist_or_not(scheduler, name):
            sched_job_delete(scheduler, name)
            cron_logger.info("任务已被关闭，从调度器中删除定时任务【{0}】,命令为：{1}，定时为：{2}。".format(name, remote_cmd, cron_exp))
    cron_logger.info("新增后--调度器最新任务列表：" + str(sched_jobs_get(scheduler)))
    return redirect("/cron/job")


def cron_job_delete(request, nid):
    """已加入调度器中的定时任务"""
    job_id = CronJobs.objects.all().filter(id=nid)
    if (nid is None) or (len(job_id) < 1):
        message = "删除定时任务对应ID不存在或者为空，请刷新后尝试"
        # return render(request, "error.html", {"error_message": message})
    else:
        job = CronJobs.objects.all().filter(id=nid).first()
        name = job.name
        cmd = job.remote_cmd
        CronJobs.objects.all().filter(id=nid).delete()
        log_str = "删除定时任务【{0}】，命令：{1}".format(name, cmd)
        logger.info(log_str)
        message = "定时任务【{0}】已删除成功，\n任务命令：{1}。".format(name, cmd)
        # 判断调度器内是否已经启用了此任务，有的话需要一起删除
        if sched_job_exist_or_not(scheduler, name):
            cron_logger.info("定时任务【{0}】已删除成功，任务命令：{1}。".format(name, cmd) + "即将从调度器中删除已存在的任务。")
            sched_job_delete(scheduler, name)
            cron_logger.info("调度器最新任务列表：" + str(sched_jobs_get(scheduler)))

    return HttpResponse(message)


def cron_job_update(request, nid):
    """已加入调度器中的定时任务"""
    job = CronJobs.objects.all().filter(id=nid).first()
    flag_choice = CronJobs.flag_choice
    error_message = ''
    if request.method == "GET":
        return render(request, "cron_job_update.html",
                      {"job": job, 'flag_choice': flag_choice, 'error_message': error_message,
                       'navbarflag': "cron"})
    # name = request.POST.get('name')
    remote_ip = request.POST.get('remote_ip')
    remote_port = request.POST.get('remote_port')
    remote_cmd = request.POST.get('remote_cmd')
    remote_name = request.POST.get('remote_name')
    remote_password = request.POST.get('remote_password')
    timeout = request.POST.get('timeout')
    cron_exp = request.POST.get('cron_exp')
    use_flag = request.POST.get('use_flag')
    comment = request.POST.get('comment')
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    CronJobs.objects.filter(id=nid).update(remote_ip=remote_ip, remote_port=remote_port,
                                           remote_cmd=remote_cmd,
                                           remote_name=remote_name, remote_password=remote_password, timeout=timeout,
                                           cron_exp=cron_exp, use_flag=use_flag, comment=comment,
                                           update_time=update_time)
    way = "调度器定时触发"
    cron_logger.info("修改前--调度器最新任务列表：" + str(sched_jobs_get(scheduler)))
    if use_flag == 'Y':
        # 判断目前调度器里是否存在,如果存在先删掉，再添加新的
        if sched_job_exist_or_not(scheduler, job.name):
            sched_job_delete(scheduler, job.name)
            cron_logger.info("脚本任务已被修改,调度器已删除旧配置的定时任务【{0}】".format(job.name))
        # sched_job_add(scheduler,
        #               shell_script_execute, (remote_ip, remote_port, remote_name, remote_password,
        #                                      timeout, remote_cmd, cron_exp, job.name, way),
        #               job.cron_exp, job.name)
        # 为避免调度器莫名其妙任务不跑，暂定每次新增修改都自动初始化一下调度器
        sched_jobs_reload(scheduler)
        cron_logger.info("脚本任务已被修改，新增定时任务【{0}】到调度器中,命令为：{1}，定时为：{2}。".format(job.name, remote_cmd, cron_exp))
    else:
        # 判断目前调度器里是否存在
        if sched_job_exist_or_not(scheduler, job.name):
            sched_job_delete(scheduler, job.name)
            cron_logger.info("脚本任务已被关闭，从调度器中删除定时脚本任务【{0}】".format(job.name))
    cron_logger.info("修改后--调度器最新任务列表：" + str(sched_jobs_get(scheduler)))
    return redirect("/cron/job")


def cron_fun_job_update(request, nid):
    """修改内部业务函数的定时、用途、参数等。函数传参请使用元组或者列表，空的就()或[]"""
    job = CronFunctionJobs.objects.all().filter(id=nid).first()
    flag_choice = CronFunctionJobs.flag_choice
    error_message = ''
    if request.method == "GET":
        return render(request, "cron_fun_job_update.html",
                      {"job": job, 'flag_choice': flag_choice, 'error_message': error_message,
                       'navbarflag': "cron"})
    fun_args = request.POST.get('fun_args')
    cron_exp = request.POST.get('cron_exp')
    use_flag = request.POST.get('use_flag')
    purpose = request.POST.get('purpose')
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    CronFunctionJobs.objects.filter(id=nid).update(fun_args=fun_args, cron_exp=cron_exp, use_flag=use_flag,
                                                   purpose=purpose, update_time=update_time)
    way = "调度器定时触发"
    cron_logger.info("修改前--调度器最新任务列表：" + str(sched_jobs_get(scheduler)))
    if use_flag == 'Y':
        if sched_job_exist_or_not(scheduler, job.fun_name):
            sched_job_delete(scheduler, job.fun_name)
            cron_logger.info("内部业务函数任务【{0}】已被修改,调度器已删除旧配置的定时任务".format(job.fun_name))
        sched_jobs_reload(scheduler)
        cron_logger.info("内部业务函数任务【{0}】已被修改，新配置已更新到调度器中,传参为：{1}，定时为：{2}。".format(job.fun_name, fun_args, cron_exp))
    else:
        # 判断目前调度器里是否存在
        if sched_job_exist_or_not(scheduler, job.fun_name):
            sched_job_delete(scheduler, job.fun_name)
            cron_logger.info("内部业务函数任务【{0}】已被关闭，已从调度器中删除定时任务".format(job.fun_name))
    cron_logger.info("修改后--调度器最新任务列表：" + str(sched_jobs_get(scheduler)))
    return redirect("/cron/job")


def cron_job_reload(request):
    """定时任务重新装载"""
    sched_jobs_reload(scheduler)
    return redirect("/cron/job")


def cron_job_history(request):
    """定时任务执行历史查看"""
    # 限制结果数量，避免记录过多
    cron_job_his_all = CronJobsHistory.objects.all().order_by('-start_time')[:200]
    return render(request, "cron_job_history.html",
                  {"job_his": cron_job_his_all, 'navbarflag': "cron"})


def cron_job_help(request):
    """定时任务帮助"""
    return render(request, "cron_job_help.html", {'navbarflag': "cron"})


def db_session(request):
    """宝山20.2数据库常用线程相关查询"""
    cur_ses_count = Oracle.orc_session_count()
    cur_max_ses_set = Oracle.orc_max_session_set()
    cur_nosys_ses_count = Oracle.orc_no_sys_session_count()
    cur_ses_active = Oracle.orc_active_session_count()
    cur_pro_count = Oracle.orc_process_count()
    cur_max_pro_set = Oracle.orc_max_process_set()

    orc_service_sess_list = Oracle.orc_service_sess_list()
    return render(request, "db_session.html", {'cur_ses_count': cur_ses_count, 'cur_max_ses_set': cur_max_ses_set,
                                               'cur_nosys_ses_count': cur_nosys_ses_count,
                                               'cur_ses_active': cur_ses_active,
                                               'cur_pro_count': cur_pro_count, 'cur_max_pro_set': cur_max_pro_set,
                                               'orc_service_sess_list': orc_service_sess_list, 'navbarflag': "db"})


def db_deadlock(request):
    """宝山20.2数据库常用线程相关查询"""
    deadlock_list = Oracle.orc_deadlock_list()
    count = len(deadlock_list)
    return render(request, "db_deadlock.html", {'count': count, 'deadlock_list': deadlock_list, 'navbarflag': "db"})


def db_tablespace(request):
    """宝山20.2数据库表空间相关查询"""
    tablespace_total = Oracle.orc_tablespace_total()
    tablespace_file = Oracle.orc_tablespace_file()
    sga_pga = Oracle.orc_sga_pga()
    return render(request, "db_tablespace.html",
                  {'sga_pga': sga_pga, 'tablespace_total': tablespace_total, 'tablespace_file': tablespace_file,
                   'navbarflag': "db"})
