from django.db import models
import uuid
# Create your models here.
class Document(models.Model):
    documentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.FileField()

class Entity(models.Model):
    entityID = models.URLField(primary_key=True)
    abstract = models.TextField()

class Instance(models.Model):
    instanceID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documentID = models.ForeignKey('Document',on_delete=models.CASCADE)
    entityID = models.ForeignKey('Entity', on_delete=models.CASCADE)
    start = models.IntegerField()
    stop = models.IntegerField()

