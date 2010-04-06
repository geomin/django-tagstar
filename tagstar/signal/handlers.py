from django.db.models import F
import tagstar

def item_tagged(sender, content_type, action, instance, tags, **kwargs):
    tags_ids = [x.pk for x in tags]

    if action == 'remove':
        tagstar.models.Tag.objects.filter(pk__in=tags_ids).update(count=F('count')-1)
    elif action == 'create':    
        tagstar.models.Tag.objects.filter(pk__in=tags_ids).update(count=F('count')+1)

def post_save(sender, instance, created, **kwargs):
    if not created:
        return

    if hasattr(instance, '_tags_field_name'):
        tags = getattr(instance, instance._tags_field_name)
        if tags:
            instance.update_tags(tags)

def post_init(sender, instance, **kwargs):
    if hasattr(instance, '_tags_field_name'):    
        setattr(instance, '_init_tags', getattr(instance, instance._tags_field_name) )

def item_created(sender, instance, created, **kwargs):
    if created:    
        model_tag, c = tagstar.models.ModelTag.objects.get_or_create(tag=instance.tag, content_type=instance.content_type)
        tagstar.models.ModelTag.objects.filter(pk=model_tag.pk).update(count=F('count')+1)

def item_deleted(sender, instance, **kwargs):
    if tagstar.utils.is_tagstar_maintained(instance):
        instance.update_tags('')
    elif isinstance(instance, tagstar.models.Item):
        model_tag = tagstar.models.ModelTag.objects.get(tag=instance.tag, content_type=instance.content_type)
        tagstar.models.ModelTag.objects.filter(pk=model_tag.pk).update(count=F('count')-1)


