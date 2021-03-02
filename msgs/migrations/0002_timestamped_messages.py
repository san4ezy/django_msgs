from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='msg',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='msg',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='msg',
            name='context',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
