from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0004_default_templates_datamigration'),
    ]

    operations = [
        migrations.AddField(
            model_name='tpl',
            name='name',
            field=models.CharField(max_length=64, default='default_name'),
        ),
        migrations.AddField(
            model_name='tpl',
            name='notes',
            field=models.CharField(max_length=128, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tpl',
            name='type',
            field=models.CharField(max_length=16, choices=[('email', 'email'), ('sms', 'sms'), ('messenger', 'messenger')], blank=True, null=True),
        ),
    ]
