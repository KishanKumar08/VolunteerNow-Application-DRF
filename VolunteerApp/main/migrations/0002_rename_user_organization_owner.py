# Generated by Django 5.0.6 on 2024-08-01 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organization',
            old_name='user',
            new_name='owner',
        ),
    ]