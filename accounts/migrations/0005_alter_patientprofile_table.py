# Generated by Django 5.1.6 on 2025-02-28 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_doctorprofile_account_id'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='patientprofile',
            table='patient_age',
        ),
    ]
