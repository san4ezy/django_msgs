from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0002_timestamped_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='msg',
            name='provider_id',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='msg',
            name='provider_response',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='msg',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'In queue'), (1, 'Sent'), (2, 'Error'), (3, 'Delivered'), (4, 'Rejected'), ], default=0),
        ),
    ]
