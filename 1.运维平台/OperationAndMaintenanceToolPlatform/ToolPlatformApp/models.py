from django.db import models


# Create your models here.

class FmAlarmEmail(models.Model):
    flag_choice = (
        ('Y', '是'),
        ('N', '否'),
    )
    id = models.AutoField('序号', primary_key=True)
    name = models.CharField('姓名', max_length=20, null=True)
    email = models.EmailField('邮箱地址', max_length=30, blank=False, unique=True)
    use_flag = models.CharField('是否启用', max_length=1, choices=flag_choice, default='Y')
    comment = models.CharField('备注', max_length=30, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = "OMP_FM_ALARM_EMAIL"
        verbose_name = 'FM报警发送邮箱列表'
        verbose_name_plural = verbose_name


class FmAlarmEmailConfig(models.Model):
    id = models.AutoField('序号', primary_key=True)
    name = models.CharField('配置名称', max_length=10, blank=False, unique=True)
    value = models.CharField('配置值', max_length=30, blank=False)
    comment = models.CharField('参数项备注', max_length=30, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = "OMP_FM_ALARM_EMAIL_CONFIG"
        verbose_name = 'FM报警通知间隔、报警数量边界等配置'
        verbose_name_plural = verbose_name


class CronJobs(models.Model):
    flag_choice = (
        ('Y', '是'),
        ('N', '否'),
    )
    job_status = (
        ('Y', '执行中'),
        ('N', '就绪'),
    )
    id = models.AutoField('序号', primary_key=True)
    name = models.CharField('job名称', max_length=30, blank=False, unique=True)
    remote_ip = models.CharField('远程服务器IP', max_length=15, blank=False)
    remote_port = models.CharField('远程服务器端口', max_length=5, blank=False)
    remote_cmd = models.CharField('完整执行命令', max_length=100, blank=False)
    remote_name = models.CharField('远程服务器用户名', max_length=15, blank=False)
    remote_password = models.CharField('远程服务器密码', max_length=15, blank=False)
    timeout = models.CharField('脚本执行超时设置,单位秒', max_length=5, default=300)
    cron_exp = models.CharField('标准cron表达式', max_length=30, blank=False)
    use_flag = models.CharField('是否启用', max_length=1, choices=flag_choice, default='N')
    current_status = models.CharField('当前是否在执行', max_length=1, choices=job_status, default='N')
    comment = models.CharField('注释', max_length=50, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = "OMP_CRON_JOBS"
        verbose_name = '运维平台定时任务的配置'
        verbose_name_plural = verbose_name


class CronJobsHistory(models.Model):
    result_choice = (
        ('Y', '成功'),
        ('N', '失败'),
    )
    object_id = models.AutoField('序号', primary_key=True)
    job_id = models.IntegerField('job主键', blank=False)
    job_name = models.CharField('job名称', max_length=30, blank=False)
    job_detail = models.CharField('用户名@IP：命令', max_length=200, blank=False)
    result = models.CharField('本次运行结果', max_length=1, choices=result_choice)
    err_mess = models.CharField('报错信息', max_length=2000, null=True, blank=True)
    start_time = models.DateTimeField('本次开始时间')
    end_time = models.DateTimeField('本次结束时间', null=True, blank=True)

    class Meta:
        db_table = "OMP_CRON_JOBS_HIST"
        verbose_name = '存放定时任务执行历史记录'
        verbose_name_plural = verbose_name


class CronFunctionJobs(models.Model):
    flag_choice = (
        ('Y', '是'),
        ('N', '否'),
    )
    id = models.AutoField('序号', primary_key=True)
    fun_name = models.CharField('内部业务函数名称', max_length=30, blank=False, unique=True)
    fun_args = models.CharField('内部函数传参（元组格式）', max_length=50,  default='()')
    cron_exp = models.CharField('标准cron表达式', max_length=30, blank=False)
    use_flag = models.CharField('是否启用', max_length=1, choices=flag_choice, default='N')
    purpose = models.CharField('作用/用途', max_length=50, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = "OMP_CRON_FUN_JOBS"
        verbose_name = '运维平台内部函数定时任务'
        verbose_name_plural = verbose_name
