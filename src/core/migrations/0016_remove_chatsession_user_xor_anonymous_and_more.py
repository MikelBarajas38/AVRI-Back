# Generated by Django 5.1.8 on 2025-04-18 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_chatsession_user_xor_anonymous'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='chatsession',
            name='user_xor_anonymous',
        ),
        migrations.RemoveField(
            model_name='chatsession',
            name='anonymous_session_id',
        ),
        migrations.AddField(
            model_name='user',
            name='anonymous_id',
            field=models.UUIDField(blank=True, default=None, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_anonymous',
            field=models.BooleanField(default=False),
        ),
    ]
