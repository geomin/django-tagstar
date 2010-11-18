from django.db.models.fields import CharField
from tagstar import managers
from tagstar.form.fields import TagsField as FormTagsField
from django.contrib.contenttypes.generic import GenericRelation
from tagstar.models import Item

class TagsField(CharField):
    """
        Denormalized Tags, will be stored as "tag1,tag2,tag3" etc.
    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 255
        kwargs['db_index']   = True
        kwargs['null']       = kwargs.get('null', True)
        kwargs['blank']      = kwargs.get('blank', True)

        if kwargs['null']:
            kwargs['default'] = ''
        else:
            kwargs['default'] = None


        super(TagsField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, main_cls, name):
        super(TagsField, self).contribute_to_class(main_cls, name)

        class Manager(managers.ItemManager):
            pass

        #Respect the manager
        if hasattr(main_cls, 'objects'):
            class Manager(main_cls.objects.__class__, managers.ItemManager):
                pass

        def get_tags(cls): 
            return cls.__class__.objects.get_tags(cls)

        def add_tags(cls, tags):
            tags = cls.__class__.objects.add_tags(cls, tags)
            tags_list = cls.tags_list
            tags_str = ",".join(set(tags+tags_list))
            value = tags_str or None
            cls.__class__.objects.filter(pk=cls.pk).update( **{'%s'% cls._tags_field_name: value} )
            cls._init_tags = tags_str
            setattr(cls, cls._tags_field_name, value)
            return tags

        def update_tags(cls, tags):
            tags = cls.__class__.objects.update_tags(cls, tags)
            tags_list = cls.tags_list
            tags_str = ",".join(set(tags+tags_list))

            value = tags_str or None

            cls.__class__.objects.filter(pk=cls.pk).update( **{'%s'% cls._tags_field_name: value} )
            cls._init_tags = tags_str
            setattr(cls, cls._tags_field_name, value)

            return tags

        def remove_tags(cls, tags):
            tags = cls.__class__.objects.remove_tags(cls, tags)
            tags_list = cls.tags_list
            tags_str = ",".join(set(tags_list)-set(tags))
            value = tags_str or None
            cls.__class__.objects.filter(pk=cls.pk).update( **{'%s'% cls._tags_field_name: value} )
            cls._init_tags = tags_str
            setattr(cls, cls._tags_field_name, value)
            return tags

        def get_related(cls):
            return cls.__class__.objects.get_related(cls)

        def _tags_list(cls):
            tags = getattr(cls, name)
            return tags and tags.split(',') or []

        main_cls.add_to_class('objects', Manager() )
        main_cls.add_to_class('_tags_field_name', name)
        main_cls.add_to_class('generic', GenericRelation(Item, content_type_field='content_type', object_id_field='object_id') )
        main_cls.add_to_class('add_tags',    add_tags )
        main_cls.add_to_class('update_tags', update_tags )
        main_cls.add_to_class('remove_tags', remove_tags )
        main_cls.add_to_class('get_related', get_related )
        main_cls.add_to_class('get_tags',    get_tags ) 
        main_cls.add_to_class('tags_list',  property(_tags_list) )         

    def formfield(self, **kwargs):
        defaults = {'form_class': FormTagsField}
        defaults.update(kwargs)
        return super(TagsField, self).formfield(**defaults)
    
    def get_internal_type(self):
        return 'CharField'


