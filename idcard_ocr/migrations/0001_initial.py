# Generated by Django 3.1.8 on 2021-06-30 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegistInfo',
            fields=[
                ('idnum', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('path', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=30)),
                ('image', models.CharField(default='', max_length=50)),
            ],
        ),
    ]
