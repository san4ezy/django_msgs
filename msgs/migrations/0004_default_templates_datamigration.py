from django.db import migrations, models


DEFAULT_KEY = 'default'


def create_default_template(apps, schema_editor):
    model = apps.get_model('msgs', 'Tpl')
    if model.objects.count() > 0:
        return  # do nothing if at least one template exists
    model.objects.get_or_create(
        key=DEFAULT_KEY,
        subject_en='Default',
        body_en='Hello! This is a default template.',
    )


def delete_default_template(apps, schema_editor):
    model = apps.get_model('msgs', 'Tpl')
    # delete the default template only
    if model.objects.count() == 1 and model.objects.last().key == DEFAULT_KEY:
        model.objects.last().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0003_provider_fields_and_statuses'),
    ]

    operations = [
        migrations.RunPython(create_default_template, delete_default_template)
    ]
