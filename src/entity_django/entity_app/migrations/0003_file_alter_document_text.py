# Generated by Django 4.1.2 on 2022-10-28 12:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('entity_app', '0002_alter_document_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('fileID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.FileField(upload_to='')),
            ],
        ),
        migrations.AlterField(
            model_name='document',
            name='text',
            field=models.TextField(),
        ),
    ]