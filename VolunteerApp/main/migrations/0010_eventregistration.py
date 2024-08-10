# Generated by Django 5.0.6 on 2024-08-09 06:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('register_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventregistration', to='main.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eventregistration', to='main.userprofile')),
            ],
        ),
    ]