# Generated by Django 4.0.4 on 2022-06-02 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ToolPlatformApp', '0003_alter_cronjobshistory_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronjobshistory',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='本次结束时间'),
        ),
    ]
