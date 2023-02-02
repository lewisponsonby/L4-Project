# Generated by Django 4.1.2 on 2023-01-29 17:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('entity_app', '0014_entity_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicDocument',
            fields=[
                ('topicDocumentID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('topicNumber', models.IntegerField()),
                ('weight', models.FloatField(null=True)),
                ('documentID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entity_app.document')),
            ],
        ),
    ]
