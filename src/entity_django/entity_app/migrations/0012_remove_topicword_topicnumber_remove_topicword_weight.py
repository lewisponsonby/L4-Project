# Generated by Django 4.1.2 on 2023-01-28 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity_app', '0011_remove_topic_topicwordid_topicword_topicnumber_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topicword',
            name='topicNumber',
        ),
        migrations.RemoveField(
            model_name='topicword',
            name='weight',
        ),
    ]