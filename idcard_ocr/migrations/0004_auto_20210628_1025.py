# Generated by Django 3.1.8 on 2021-06-28 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idcard_ocr', '0003_userinfo_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='image',
            field=models.CharField(default='', max_length=100),
        ),
    ]
