"""OperationAndMaintenanceToolPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ToolPlatformApp import views

urlpatterns = [
    path('', views.home),
    # path('home', views.home),
    # Eureka
    path('eureka', views.eureka_get),
    path('eureka/delete', views.eureka_delete),
    # flowmeter alarm number mail
    path('fm/email', views.fm_email),
    path('fm/email/add', views.fm_email_add),
    path('fm/email/<int:nid>/delete', views.fm_email_delete),
    path('fm/email/<int:nid>/update', views.fm_email_update),
    # crontab job
    path('cron/job', views.cron_job),
    path('cron/job/add', views.cron_job_add),
    path('cron/job/<int:nid>/delete', views.cron_job_delete),
    path('cron/job/<int:nid>/update', views.cron_job_update),
    path('cron/fun_job/<int:nid>/update', views.cron_fun_job_update),
    path('cron/job/reload', views.cron_job_reload),
    path('cron/job/history', views.cron_job_history),
    path('cron/job/help', views.cron_job_help),

    # 数据库线程等常用查询
    path('db/session', views.db_session),
    path('db/deadlock', views.db_deadlock),
    path('db/tablespace', views.db_tablespace),
]
