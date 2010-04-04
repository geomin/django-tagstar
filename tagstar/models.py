from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from tagstar.signal import signals
from tagstar.signal import handlers
from django.db.models.signals import post_save, post_init, post_delete

class Tag(models.Model):
    name  = models.CharField(max_length=32, unique=True)
    count = models.PositiveIntegerField(default=0)      #how many times was this tagged

    def __unicode__(self):
        return "%s - %d" % (self.name, self.count)
    
class Item(models.Model):
    tag             = models.ForeignKey(Tag)
    content_type    = models.ForeignKey(ContentType)
    object_id       = models.PositiveIntegerField(db_index=True)
    
    content_object  = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        unique_together = (('tag', 'content_type', 'object_id'),)
    
    def __unicode__(self):
        return "%s - {%s}" % (self.content_type.name, self.tag) 

class ModelTag(models.Model):
    tag          = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType) 
    count        = models.PositiveIntegerField(default=0) #how many times was this tagged

    class Meta:
        unique_together = (('tag', 'content_type'),)

signals.item_tagged.connect( handlers.item_tagged )
post_save.connect(handlers.item_created, sender=Item)
post_delete.connect(handlers.item_deleted)
post_save.connect(handlers.post_save)
post_init.connect(handlers.post_init)
