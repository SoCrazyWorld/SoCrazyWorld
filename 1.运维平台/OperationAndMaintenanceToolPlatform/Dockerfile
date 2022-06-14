FROM wmnode6.icity.inesa.com/python3_base_zlw:latest
RUN mkdir /application
WORKDIR  /application
COPY ./OperationAndMaintenanceToolPlatform.zip /application/
RUN unzip OperationAndMaintenanceToolPlatform.zip
RUN rm OperationAndMaintenanceToolPlatform.zip
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
RUN pip install APScheduler==3.9.1
RUN pip install paramiko==2.11.0
ENTRYPOINT  python manage.py runserver 0.0.0.0:8000
#ENTRYPOINT service cron start  &&  python manage.py runserver 0.0.0.0:8000 && python manage.py crontab add