# Generated by Django 5.1.7 on 2025-04-18 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_chatsession_anonymous_session_id'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='chatsession',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('anonymous_session_id__isnull', True), ('user__isnull', False)), models.Q(('anonymous_session_id__isnull', False), ('user__isnull', True)), _connector='OR'), name='user_xor_anonymous'),
        ),
    ]
