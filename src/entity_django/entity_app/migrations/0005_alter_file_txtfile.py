# Generated by Django 4.1.2 on 2022-10-28 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entity_app', '0004_rename_text_file_txtfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='txtfile',
            field=models.FileField(upload_to='entity_app/static/textfiles/'),
        ),
    ]
