from django.db import models
import uuid
# Create your models here.
class File(models.Model):
    fileID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    txtfile = models.FileField(upload_to='entity_app/static/textfiles/')

class Document(models.Model):
    documentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.TextField()
    filetitle = models.TextField(null=True)
    text = models.TextField()
    tokens = models.TextField(null=True)

class Entity(models.Model):
    entityID = models.URLField(primary_key=True)
    text = models.TextField(null=True)
    abstract = models.TextField()
    sensitivity = models.IntegerField(default=0, editable=True)

class Instance(models.Model):
    instanceID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documentID = models.ForeignKey('Document',on_delete=models.CASCADE)
    entityID = models.ForeignKey('Entity', on_delete=models.CASCADE)
    start = models.IntegerField()
    stop = models.IntegerField()

class TopicWord(models.Model):
    topicWordID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entityID = models.ForeignKey('Entity', on_delete=models.CASCADE)
    topicNumber = models.IntegerField()
    weight = models.FloatField(null=True)

class TopicDocument(models.Model):
    topicDocumentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documentID = models.ForeignKey('Document', on_delete=models.CASCADE)
    topicNumber = models.IntegerField()
    weight = models.FloatField(null=True)

