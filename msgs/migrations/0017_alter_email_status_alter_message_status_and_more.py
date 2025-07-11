# Generated by Django 5.0.6 on 2025-07-07 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0016_alter_email_error_alter_message_error_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='status',
            field=models.CharField(choices=[('in_queue', 'In Queue'), ('sent', 'Sent'), ('error', 'Error'), ('delivered', 'Delivered'), ('rejected', 'Rejected'), ('opened', 'Opened'), ('spam_reported', 'Spam Reported')], default='in_queue', max_length=16),
        ),
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.CharField(choices=[('in_queue', 'In Queue'), ('sent', 'Sent'), ('error', 'Error'), ('delivered', 'Delivered'), ('rejected', 'Rejected'), ('opened', 'Opened'), ('spam_reported', 'Spam Reported')], default='in_queue', max_length=16),
        ),
        migrations.AlterField(
            model_name='sms',
            name='status',
            field=models.CharField(choices=[('in_queue', 'In Queue'), ('sent', 'Sent'), ('error', 'Error'), ('delivered', 'Delivered'), ('rejected', 'Rejected'), ('opened', 'Opened'), ('spam_reported', 'Spam Reported')], default='in_queue', max_length=16),
        ),
    ]
