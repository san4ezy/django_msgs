from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0005_tpl_name_and_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tpl',
            name='name',
            field=models.CharField(default='default name', max_length=64),
        ),
        migrations.AlterField(
            model_name='tpl',
            name='type',
            field=models.CharField(blank=True, choices=[('email', 'Email'), ('sms', 'Sms'), ('messenger', 'Messenger')], max_length=16, null=True),
        ),
    ]