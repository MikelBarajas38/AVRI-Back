# Generated by Django 5.1.7 on 2025-04-18 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_authoreddocument_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='anonymous_session_id',
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
    ]
