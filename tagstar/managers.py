from django.db import models
from tagstar.models import Item, Tag, ModelTag
from tagstar.signal.signals import item_tagged
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from tagstar.utils import is_string, is_list_or_tuple, string_to_list, is_tagstar_maintained, escape_tags
from django.db.models import Q
from tagstar.exceptions import ItemNotTagstarMaintained

class ItemManager(models.Manager):

    def get_tags(self, instance_list=None):
        """
        instance_list = single object or object list
        Return all the tags for the Model if instance_list is None or return tags for instance_list
        """
        ctype = ContentType.objects.get_for_model(self.model)
        
        qs = Tag.objects.extra(select={'model_count':'tagstar_modeltag.count'}
                              ).filter(modeltag__content_type__pk=ctype.id, count__gt=0)

        if instance_list:                   
            if not is_list_or_tuple(instance_list):
                qs = Tag.objects.filter(item__content_type__pk=ctype.id, item__object_id=instance_list.pk)
            else:
                qs = Tag.objects.filter(item__content_type__pk=ctype.id, item__object_id__in=[x.pk for x in instance_list])
        
        return qs

    def get_related(self, instance):
        """
        Returns all the related items
        """
        if not is_tagstar_maintained(instance):
            raise ItemNotTagstarMaintained("Item %s is not under Tagstar" % instance.__class__)

        return self.get_related_by_tags(getattr(instance, instance._tags_field_name), instance)

    def get_related_by_tags(self, tags, instance=None):
        """
        Return all items which have given tags
        instance = exclude pk
        """
        if is_string(tags):
            tags = tags.split(',')

        tags = escape_tags(tags)
        tags = '|'.join(tags)
        
        qs = self.model.objects.filter(**{'%s__regex' % self.model._tags_field_name: r'(%s)' % tags })

        if instance is not None:
            qs = qs.exclude(pk=instance.pk)

        return qs

    def get_tagless_items(self):
        """
        Return items which are tagless
        """
        return self.filter(**{'%s__isnull' % self.model._tags_field_name: True})
    
    def get_related_by_tags_q(self, tags, q):
        """
        Returns all items with given tags with the Q object
        """
        if is_string(tags):
            tags = tags.split(',')

        tags = escape_tags(tags)
        tags = '|'.join(tags)

        q = Q(tags__regex=r'(%s)' % tags) | q

        return self.model.objects.filter(q)

    def add_tags(self, instance, tags):
        """
        Add tags to item
        """
        if is_string(tags):
            tags = string_to_list(tags)

        new_tags = [ Tag.objects.get_or_create(name=x.strip().lower())[0] for x in (set(tags) - set(instance.tags_list)) if x.strip() ]
        self._add_tags(instance, new_tags)

    def _add_tags(self, instance, new_tags):
        if not new_tags:
            return []

        ctype         = ContentType.objects.get_for_model(instance)
        #Create mapping
        for x in new_tags:
            Item.objects.create(content_object=instance, tag=x)
        
        tags = set(instance.tags_list + [x.name for x in new_tags])

        #send signal
        item_tagged.send(sender=self.model, action='create', content_type=ctype, tags=new_tags, instance=instance)

        return new_tags

    def remove_tags(self, instace, tags):
        """
        Remove given tags
        """
        if is_string(tags):
            tags = string_to_list(tags)

        tags = set([x.strip().lower() for x in tags if x.strip() ])
        tags = [x for x in instace.tags_list for y in tags if x == y]

        if not tags:
            return []

        obsolete_tags = Tag.objects.filter(name__in=tags )

        self._remove_tags(instace, obsolete_tags)

    def _remove_tags(self, instance, tags):
        if not tags:
            return []

        ctype = ContentType.objects.get_for_model(instance)
        #Delete mapping            
        Item.objects.filter(content_type__pk=ctype.id, 
                            object_id=instance.pk, 
                            tag__in=[x.pk for x in tags]
                            ).delete()

        new_tags = set(instance.tags_list) - set([x.name for x in tags]) 
        
        #send signal
        item_tagged.send(sender=self.model, action='remove', content_type=ctype, tags=tags, instance=instance)

        return tags

    def update_tags(self, instance, tags):
        """
        Update tags from an item
        """
        if not is_tagstar_maintained(instance):
            raise ItemNotTagstarMaintained("Item %s is not under Tagstar" % instance.__class__)
        
        if is_string(tags):
            tags = string_to_list(tags)

        tags          = set([x.strip().lower() for x in tags])        
        instance_tags = instance._init_tags and set([ x.strip().lower() for x in instance._init_tags.split(',')]) or set()        
        
        if instance_tags != tags:          
            new_tags      = set( Tag.objects.get_or_create(name=x.strip().lower())[0] for x in (tags - instance_tags) if x.strip() )
            obsolete_tags = Tag.objects.filter(name__in=(instance_tags - tags) )
            self._add_tags(instance, new_tags)
            self._remove_tags(instance, obsolete_tags)
            
        return tags
