# Generated by Django 2.1.4 on 2018-12-20 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_emailverifyrecord_update_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailverifyrecord',
            name='update_email',
        ),
        migrations.AddField(
            model_name='emailverifyrecord',
            name='user_email',
            field=models.EmailField(default='', max_length=50, verbose_name='用户原来的邮箱'),
        ),
    ]
