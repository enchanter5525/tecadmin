# Generated by Django 3.2.5 on 2021-07-14 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('uid', models.UUIDField(auto_created=True, primary_key=True, serialize=False, unique=True)),
                ('timestamp', models.DateTimeField(max_length=20)),
                ('activity', models.CharField(max_length=50)),
                ('ip_address', models.GenericIPAddressField()),
                ('device_env', models.CharField(max_length=150)),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.tecuser')),
            ],
        ),
    ]
