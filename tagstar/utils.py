from re import escape as re_escape

def is_string(obj):
    return type(obj) in (type(''), type(u''))

def is_list_or_tuple(obj):
    return type(obj) in ( type(tuple()),  type(list()) )

def string_to_list(string):
    return string.replace(',', ' ').strip().split(' ')

def is_tagstar_maintained(instance):
    return hasattr(instance, '_tags_field_name') and hasattr(instance, instance._tags_field_name)

def escape_tags(tags_list):
    return [ re_escape(x) for x in tags_list]
