# Generated by Django 5.1.6 on 2025-03-02 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_user_city'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='city',
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='city',
            field=models.CharField(default='Default', max_length=255),
        ),
    ]
